import { Request, Response, NextFunction } from 'express';
import crypto from 'crypto';

// Configuration interface for flexible nonce middleware
export interface NonceConfig {
  headerName?: string;
  maxNonceAge?: number;
  nonceLength?: number;
  excludedMethods?: string[];
}

export class NonceMiddleware {
  private config: Required<NonceConfig>;
  private nonceStore: Map<string, number>;

  constructor(config: NonceConfig = {}) {
    // Default configuration with sensible defaults
    this.config = {
      headerName: 'X-Nonce',
      maxNonceAge: 5 * 60 * 1000, // 5 minutes
      nonceLength: 32, // 32 bytes = 64 hex characters
      excludedMethods: ['GET', 'HEAD', 'OPTIONS'],
      ...config
    };

    this.nonceStore = new Map();
  }

  /**
   * Generate a cryptographically secure nonce
   * @returns {string} Hex-encoded nonce
   */
  private generateNonce(): string {
    return crypto.randomBytes(this.config.nonceLength).toString('hex');
  }

  /**
   * Remove expired nonces from the store
   */
  private cleanupExpiredNonces(): void {
    const now = Date.now();
    for (const [nonce, timestamp] of this.nonceStore.entries()) {
      if (now - timestamp > this.config.maxNonceAge) {
        this.nonceStore.delete(nonce);
      }
    }
  }

  /**
   * Validate and consume a nonce
   * @param nonce Nonce to validate
   * @returns {boolean} Whether the nonce is valid
   */
  private validateAndConsumeNonce(nonce: string): boolean {
    if (!nonce) return false;

    const timestamp = this.nonceStore.get(nonce);
    if (!timestamp) return false;

    // Remove the nonce after validation to prevent replay
    this.nonceStore.delete(nonce);

    return true;
  }

  /**
   * Middleware function for nonce generation and validation
   */
  public handler = (req: Request, res: Response, next: NextFunction): void => {
    try {
      // Clean up expired nonces
      this.cleanupExpiredNonces();

      // Skip nonce validation for excluded methods
      if (this.config.excludedMethods.includes(req.method)) {
        return next();
      }

      // For write methods, validate nonce
      const clientNonce = req.get(this.config.headerName);

      // Validate nonce
      if (!this.validateAndConsumeNonce(clientNonce)) {
        return res.status(403).json({
          error: 'Invalid or expired nonce',
          message: 'A valid nonce is required for this request method'
        });
      }

      next();
    } catch (error) {
      // Graceful error handling
      res.status(500).json({
        error: 'Nonce middleware error',
        message: error instanceof Error ? error.message : 'Unknown error'
      });
    }
  }

  /**
   * Generate and inject a new nonce into the response
   */
  public generateNonceHeader = (req: Request, res: Response, next: NextFunction): void => {
    // Generate a new nonce
    const nonce = this.generateNonce();

    // Store the nonce with current timestamp
    this.nonceStore.set(nonce, Date.now());

    // Set nonce in response header
    res.set(this.config.headerName, nonce);

    next();
  }
}

// Export a default instance with standard configuration
export default new NonceMiddleware();