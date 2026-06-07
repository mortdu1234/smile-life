const IOHandlers = {};

export function registerHandler(kind, fn) {
  IOHandlers[kind] = fn;
}

export function getHandler(kind) {
  return IOHandlers[kind] ?? null;
}