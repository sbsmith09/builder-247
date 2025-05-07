import NonceMiddleware, { NonceConfig } from './nonce';

// Default middleware instance
const defaultNonceMiddleware = NonceMiddleware;

export {
  NonceMiddleware,
  NonceConfig,
  defaultNonceMiddleware
};

// Expose core methods for easy use
export const nonceHandler = defaultNonceMiddleware.handler;
export const generateNonceHeader = defaultNonceMiddleware.generateNonceHeader;