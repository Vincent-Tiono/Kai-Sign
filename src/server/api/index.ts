import { createTRPCRouter, publicProcedure } from "~/server/api/trpc";

export const sample = createTRPCRouter({
  hello: publicProcedure.query(({}) => {
    return {
      greeting: `Hello`,
    };
  }),
});
