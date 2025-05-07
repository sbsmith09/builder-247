import { Request, Response, NextFunction } from 'express';
import NonceMiddleware, { NonceConfig } from '../../src/middleware/nonce';

describe('Nonce Middleware', () => {
  let mockRequest: Partial<Request>;
  let mockResponse: Partial<Response>;
  let nextFunction: NextFunction;

  // Helper to create a fresh middleware instance for each test
  const createMiddleware = (config?: NonceConfig) => 
    new NonceMiddleware(config);

  beforeEach(() => {
    mockRequest = {
      method: 'POST',
      path: '/test-endpoint',
      get: jest.fn()
    };
    mockResponse = {
      status: jest.fn().mockReturnThis(),
      json: jest.fn(),
      set: jest.fn()
    };
    nextFunction = jest.fn();
  });

  describe('Nonce Generation', () => {
    it('should generate unique nonces', () => {
      const middleware = createMiddleware();
      const generateNonceHeader = middleware.generateNonceHeader;

      generateNonceHeader(
        mockRequest as Request, 
        mockResponse as Response, 
        nextFunction
      );

      expect(mockResponse.set).toHaveBeenCalledWith(
        'X-Nonce', 
        expect.any(String)
      );
      expect(nextFunction).toHaveBeenCalled();
    });

    it('should generate different nonces for subsequent calls', () => {
      const middleware = createMiddleware();
      const generateNonceHeader = middleware.generateNonceHeader;

      // First nonce generation
      generateNonceHeader(
        mockRequest as Request, 
        mockResponse as Response, 
        nextFunction
      );
      const firstNonce = (mockResponse.set as jest.Mock).mock.calls[0][1];

      // Reset mocks
      (mockResponse.set as jest.Mock).mockClear();

      // Second nonce generation
      generateNonceHeader(
        mockRequest as Request, 
        mockResponse as Response, 
        nextFunction
      );
      const secondNonce = (mockResponse.set as jest.Mock).mock.calls[0][1];

      expect(firstNonce).not.toEqual(secondNonce);
    });
  });

  describe('Nonce Validation', () => {
    it('should validate a nonce for write methods', () => {
      const middleware = createMiddleware();
      const generateNonceHeader = middleware.generateNonceHeader;
      const handler = middleware.handler;

      // Generate a nonce
      generateNonceHeader(
        mockRequest as Request, 
        mockResponse as Response, 
        nextFunction
      );

      // Get the generated nonce
      const generatedNonce = (mockResponse.set as jest.Mock)
        .mock.calls[0][1];

      // Reset mocks
      (mockResponse.set as jest.Mock).mockClear();
      (nextFunction as jest.Mock).mockClear();

      // Simulate request with the nonce
      mockRequest.get = jest.fn().mockReturnValue(generatedNonce);

      // Validate the nonce
      handler(
        mockRequest as Request, 
        mockResponse as Response, 
        nextFunction
      );

      expect(nextFunction).toHaveBeenCalled();
      expect(mockResponse.status).not.toHaveBeenCalled();
    });

    it('should reject reused nonces', () => {
      const middleware = createMiddleware();
      const generateNonceHeader = middleware.generateNonceHeader;
      const handler = middleware.handler;

      // Generate a nonce
      generateNonceHeader(
        mockRequest as Request, 
        mockResponse as Response, 
        nextFunction
      );

      // Get the generated nonce
      const generatedNonce = (mockResponse.set as jest.Mock)
        .mock.calls[0][1];

      // Reset mocks
      (mockResponse.set as jest.Mock).mockClear();
      (nextFunction as jest.Mock).mockClear();

      // First validation (should pass)
      mockRequest.get = jest.fn().mockReturnValue(generatedNonce);
      handler(
        mockRequest as Request, 
        mockResponse as Response, 
        nextFunction
      );
      expect(nextFunction).toHaveBeenCalled();

      // Reset mocks
      (nextFunction as jest.Mock).mockClear();

      // Second validation (should fail)
      handler(
        mockRequest as Request, 
        mockResponse as Response, 
        nextFunction
      );

      expect(mockResponse.status).toHaveBeenCalledWith(403);
      expect(nextFunction).not.toHaveBeenCalled();
    });

    it('should support custom configuration', () => {
      const customConfig: NonceConfig = {
        headerName: 'Custom-Nonce-Header',
        maxNonceAge: 1000, // Very short expiration
        excludedMethods: ['GET']
      };

      const middleware = createMiddleware(customConfig);
      
      // Verify custom header is used
      expect(middleware['config'].headerName).toBe('Custom-Nonce-Header');
    });
  });

  describe('Nonce Store Management', () => {
    it('should limit nonce store size', () => {
      const middleware = createMiddleware({
        maxNonceStore: 2
      });

      const generateNonceHeader = middleware.generateNonceHeader;

      // Generate multiple nonces
      for (let i = 0; i < 5; i++) {
        generateNonceHeader(
          mockRequest as Request, 
          mockResponse as Response, 
          nextFunction
        );
      }

      // Check nonce store stats
      const stats = middleware.getNonceStoreStats();
      expect(stats.currentSize).toBe(2);
      expect(stats.maxSize).toBe(2);
    });
  });

  describe('Method Exclusion', () => {
    it('should skip nonce validation for excluded methods', () => {
      const middleware = createMiddleware({
        excludedMethods: ['GET', 'HEAD']
      });
      const handler = middleware.handler;

      // Test GET method
      mockRequest.method = 'GET';
      handler(
        mockRequest as Request, 
        mockResponse as Response, 
        nextFunction
      );

      expect(nextFunction).toHaveBeenCalled();
      expect(mockResponse.status).not.toHaveBeenCalled();
    });
  });

  describe('Error Handling', () => {
    it('should handle middleware errors gracefully', () => {
      const middleware = createMiddleware();
      const handler = middleware.handler;

      // Force an error by manipulating request
      mockRequest.get = () => { throw new Error('Test error'); };

      handler(
        mockRequest as Request, 
        mockResponse as Response, 
        nextFunction
      );

      expect(mockResponse.status).toHaveBeenCalledWith(500);
      expect(mockResponse.json).toHaveBeenCalledWith(
        expect.objectContaining({
          error: 'Nonce Middleware Error'
        })
      );
    });
  });
});