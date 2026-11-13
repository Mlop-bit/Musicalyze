export type Context = { headers: Headers };

export const createContext = ({ req }: { req: Request }): Context => ({
  headers: req.headers,
});
