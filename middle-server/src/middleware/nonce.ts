import { Request, Response, NextFunction } from 'express';
import crypto from 'crypto';

// Interface to store nonce tracking
interface NonceStore {
  [nonce: string]: number;
}

class NonceMiddleware {
  private nonceStore: NonceStore = {};
  private maxNonceAge: number; // in milliseconds

  constructor(maxNonceAge: number = 5 * 60 * 1000) { // Default 5 minutes
    this.maxNonceAge = maxNonceAge;
  }

  /**
   * Generate a unique nonce
   * @returns {string} A cryptographically secure random nonce
   */
  private generateNonce(): string {
    return crypto.randomBytes(32).toString('hex');
  }

  /**
   * Cleanup expired nonces from store
   */
  private cleanupExpiredNonces(): void {
    const now = Date.now();
    Object.keys(this.nonceStore).forEach(nonce => {
      if (now - this.nonceStore[nonce] > this.maxNonceAge) {
        delete this.nonceStore[nonce];
      }
    });
  }

  /**
   * Middleware to generate and validate nonces
   * @param req Express request object
   * @param res Express response object
   * @param next Express next function
   */
  public nonceMiddleware = (req: Request, res: Response, next: NextFunction): void => {
    // Cleanup expired nonces
    this.cleanupExpiredNonces();

    // For GET requests, generate and send a new nonce
    if (req.method === 'GET') {
      const nonce = this.generateNonce();
      this.nonceStore[nonce] = Date.now();
      res.set('X-Nonce', nonce);
      next();
      return;
    }

    // For other methods (POST, PUT, DELETE), validate the nonce
    const clientNonce = req.get('X-Nonce');

    // Check if nonce is present
    if (!clientNonce) {
      res.status(400).json({ error: 'Nonce is required' });
      return;
    }

    // Check if nonce exists and is not expired
    const nonceTimestamp = this.nonceStore[clientNonce];
    if (!nonceTimestamp) {
      res.status(400).json({ error: 'Invalid nonce' });
      return;
    }

    // Remove the nonce after use to prevent replay attacks
    delete this.nonceStore[clientNonce];

    next();
  }
}

export default new NonceMiddleware();