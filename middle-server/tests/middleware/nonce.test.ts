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
  });

  describe('Nonce Validation', () => {
    it('should allow requests with valid nonce', () => {
      const middleware = createMiddleware();
      const generateNonceHeader = middleware.generateNonceHeader;
      const handler = middleware.handler;

      // First generate a nonce
      generateNonceHeader(
        mockRequest as Request, 
        mockResponse as Response, 
        nextFunction
      );

      // Get the generated nonce
      const generatedNonce = (mockResponse.set as jest.Mock)
        .mock.calls[0][1];

      // Simulate request with the nonce
      mockRequest.get = jest.fn().mockReturnValue(generatedNonce);

      // Validate the nonce
      handler(
        mockRequest as Request, 
        mockResponse as Response, 
        nextFunction
      );

      expect(nextFunction).toHaveBeenCalled();
    });

    it('should reject requests with invalid nonce', () => {
      const middleware = createMiddleware();
      const handler = middleware.handler;

      // Simulate request with an invalid nonce
      mockRequest.get = jest.fn().mockReturnValue('invalid-nonce');

      handler(
        mockRequest as Request, 
        mockResponse as Response, 
        nextFunction
      );

      expect(mockResponse.status).toHaveBeenCalledWith(403);
      expect(mockResponse.json).toHaveBeenCalledWith(
        expect.objectContaining({
          error: 'Invalid or expired nonce'
        })
      );
    });

    it('should support custom configuration', () => {
      const customConfig: NonceConfig = {
        headerName: 'Custom-Nonce-Header',
        maxNonceAge: 1000, // Very short expiration
        nonceLength: 16
      };

      const middleware = createMiddleware(customConfig);
      const generateNonceHeader = middleware.generateNonceHeader;
      const handler = middleware.handler;

      // Generate nonce with custom header
      generateNonceHeader(
        mockRequest as Request, 
        mockResponse as Response, 
        nextFunction
      );

      // Check custom header was used
      expect(mockResponse.set).toHaveBeenCalledWith(
        'Custom-Nonce-Header', 
        expect.any(String)
      );
    });

    it('should skip nonce validation for excluded methods', () => {
      const middleware = createMiddleware({
        excludedMethods: ['GET', 'POST']
      });
      const handler = middleware.handler;

      mockRequest.method = 'GET';

      handler(
        mockRequest as Request, 
        mockResponse as Response, 
        nextFunction
      );

      expect(nextFunction).toHaveBeenCalled();
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
          error: 'Nonce middleware error'
        })
      );
    });
  });
});