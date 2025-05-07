import { Request, Response, NextFunction } from 'express';
import nonceMiddleware from '../../src/middleware/nonce';

describe('Nonce Middleware', () => {
  let mockRequest: Partial<Request>;
  let mockResponse: Partial<Response>;
  let nextFunction: NextFunction;

  beforeEach(() => {
    mockRequest = {};
    mockResponse = {
      status: jest.fn().mockReturnThis(),
      json: jest.fn(),
      set: jest.fn()
    };
    nextFunction = jest.fn();
  });

  describe('GET Requests', () => {
    beforeEach(() => {
      mockRequest.method = 'GET';
    });

    it('should generate and set a nonce for GET requests', () => {
      nonceMiddleware.nonceMiddleware(
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

  describe('POST Requests', () => {
    beforeEach(() => {
      mockRequest.method = 'POST';
    });

    it('should reject requests without a nonce', () => {
      nonceMiddleware.nonceMiddleware(
        mockRequest as Request, 
        mockResponse as Response, 
        nextFunction
      );

      expect(mockResponse.status).toHaveBeenCalledWith(400);
      expect(mockResponse.json).toHaveBeenCalledWith({ 
        error: 'Nonce is required' 
      });
    });

    it('should accept a valid nonce', () => {
      // First, generate a nonce via a GET request
      const generateNonceResponse: Partial<Response> = {
        set: (header: string, value: string) => {
          mockRequest.get = (h: string) => 
            h === 'X-Nonce' ? value : undefined;
        }
      };

      // Simulate GET request to generate nonce
      nonceMiddleware.nonceMiddleware(
        { method: 'GET' } as Request, 
        generateNonceResponse as Response, 
        nextFunction
      );

      // Now test POST request with the generated nonce
      mockRequest.method = 'POST';
      nonceMiddleware.nonceMiddleware(
        mockRequest as Request, 
        mockResponse as Response, 
        nextFunction
      );

      expect(nextFunction).toHaveBeenCalled();
    });

    it('should reject a reused nonce', () => {
      // First, generate a nonce via a GET request
      const generateNonceResponse: Partial<Response> = {
        set: (header: string, value: string) => {
          mockRequest.get = (h: string) => 
            h === 'X-Nonce' ? value : undefined;
        }
      };

      // Simulate GET request to generate nonce
      nonceMiddleware.nonceMiddleware(
        { method: 'GET' } as Request, 
        generateNonceResponse as Response, 
        nextFunction
      );

      // First POST request with nonce
      mockRequest.method = 'POST';
      nonceMiddleware.nonceMiddleware(
        mockRequest as Request, 
        mockResponse as Response, 
        nextFunction
      );

      // Reset mocks
      (mockResponse.status as jest.Mock).mockClear();
      (mockResponse.json as jest.Mock).mockClear();
      (nextFunction as jest.Mock).mockClear();

      // Second POST request with same nonce
      nonceMiddleware.nonceMiddleware(
        mockRequest as Request, 
        mockResponse as Response, 
        nextFunction
      );

      expect(mockResponse.status).toHaveBeenCalledWith(400);
      expect(mockResponse.json).toHaveBeenCalledWith({ 
        error: 'Invalid nonce' 
      });
    });
  });
});