import { type paths, type components } from "~/generate/api-types";

export type Erc7730 =
  paths["/api/py/generateERC7730"]["post"]["responses"]["200"]["content"]["application/json"];

export type Operation = Erc7730["display"]["formats"][string];

export type DateField = components["schemas"]["InputDateParameters"];

export type OperationMetadata = {
  operationName: string;
  metadata: Erc7730["metadata"] | null;
};
