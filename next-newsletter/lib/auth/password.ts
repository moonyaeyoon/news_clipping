import { pbkdf2Sync, randomBytes, timingSafeEqual } from "node:crypto";

const HASH_ALGORITHM = "pbkdf2_sha256";
const HASH_ITERATIONS = 210000;
const HASH_LENGTH = 32;
const HASH_DIGEST = "sha256";

export function hashPassword(password: string) {
  const salt = randomBytes(16).toString("base64url");
  const hash = pbkdf2Sync(
    password,
    salt,
    HASH_ITERATIONS,
    HASH_LENGTH,
    HASH_DIGEST,
  ).toString("base64url");

  return `${HASH_ALGORITHM}$${HASH_ITERATIONS}$${salt}$${hash}`;
}

export function verifyPassword(password: string, storedHash: string) {
  const [algorithm, iterations, salt, hash] = storedHash.split("$");

  if (algorithm !== HASH_ALGORITHM || !iterations || !salt || !hash) {
    return false;
  }

  const iterationCount = Number(iterations);

  if (!Number.isInteger(iterationCount) || iterationCount <= 0) {
    return false;
  }

  const expected = Buffer.from(hash, "base64url");
  const actual = pbkdf2Sync(
    password,
    salt,
    iterationCount,
    expected.length,
    HASH_DIGEST,
  );

  return expected.length === actual.length && timingSafeEqual(expected, actual);
}
