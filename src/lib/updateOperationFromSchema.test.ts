import { describe, it, expect } from "vitest";
import { updateOperationFromSchema } from "./updateOperationFromSchema";
import { type Operation } from "~/store/types";
import { type OperationFormType } from "~/app/operations/editOperation";

describe("updateOperationFromSchema", () => {
  it("should update the operation based on the updated schema and set excluded paths", () => {
    const operation: Operation = {
      $id: null,
      intent: "exampleIntent",
      screens: null,
      fields: [
        {
          path: "#._baycPairs.[]",
          value: null,
          fields: [
            {
              path: "",
              value: null,
              fields: [
                {
                  $id: null,
                  label: "Main Token Id not updated",
                  format: "raw",
                  params: null,
                  path: "mainTokenId",
                  value: null,
                },
                {
                  $id: null,
                  label: "Bakc Token Id",
                  format: "raw",
                  params: null,
                  path: "bakcTokenId",
                  value: null,
                },
              ],
            },
          ],
        },
        {
          path: "#._maycPairs.[]",
          value: null,
          fields: [
            {
              path: "",
              value: null,
              fields: [
                {
                  $id: null,
                  label: "Main Token Id not updated",
                  format: "raw",
                  params: null,
                  path: "mainTokenId",
                  value: null,
                },
                {
                  $id: null,
                  label: "Bakc Token Id",
                  format: "raw",
                  params: null,
                  path: "bakcTokenId",
                  value: null,
                },
              ],
            },
          ],
        },
        {
          $id: null,
          label: "Recipient old",
          format: "addressName",
          params: {
            types: ["eoa", "wallet"],
            sources: null,
          },
          path: "#._recipient",
          value: null,
        },
      ],
      required: null,
      excluded: null,
    };

    const updatedSchema: OperationFormType = {
      intent: "exampleIntent",
      fields: [
        {
          label: "Main Token Id",
          format: "raw",
          params: null,
          path: "#._baycPairs.[]mainTokenId",
          isIncluded: true,
          isRequired: false,
        },
        {
          label: "Bakc Token Id",
          format: "raw",
          params: null,
          path: "#._baycPairs.[]bakcTokenId",
          isIncluded: true,
          isRequired: false,
        },
        {
          label: "Main Token Id",
          format: "addressName",
          params: {
            types: ["eoa", "wallet"],
            sources: null,
          },
          path: "#._maycPairs.[]mainTokenId",
          isIncluded: false,
          isRequired: false,
        },
        {
          label: "Bakc Token Id",
          format: "raw",
          params: null,
          path: "#._maycPairs.[]bakcTokenId",
          isIncluded: true,
          isRequired: true,
        },
        {
          label: "Recipient",
          format: "addressName",
          params: {
            types: ["eoa", "wallet"],
            sources: null,
          },
          path: "#._recipient",
          isIncluded: true,
          isRequired: true,
        },
      ],
    };

    const expectedUpdatedOperation: Operation = {
      $id: null,
      intent: "exampleIntent",
      screens: null,
      fields: [
        {
          path: "#._baycPairs.[]",
          value: null,
          fields: [
            {
              path: "",
              value: null,
              fields: [
                {
                  $id: null,
                  label: "Main Token Id",
                  format: "raw",
                  params: null,
                  path: "mainTokenId",
                  value: null,
                },
                {
                  $id: null,
                  label: "Bakc Token Id",
                  format: "raw",
                  params: null,
                  path: "bakcTokenId",
                  value: null,
                },
              ],
            },
          ],
        },
        {
          path: "#._maycPairs.[]",
          value: null,
          fields: [
            {
              path: "",
              value: null,
              fields: [
                {
                  $id: null,
                  label: "Main Token Id",
                  format: "addressName",
                  params: {
                    types: ["eoa", "wallet"],
                    sources: null,
                  },
                  path: "mainTokenId",
                  value: null,
                },
                {
                  $id: null,
                  label: "Bakc Token Id",
                  format: "raw",
                  params: null,
                  path: "bakcTokenId",
                  value: null,
                },
              ],
            },
          ],
        },
        {
          $id: null,
          label: "Recipient",
          format: "addressName",
          params: {
            types: ["eoa", "wallet"],
            sources: null,
          },
          path: "#._recipient",
          value: null,
        },
      ],
      required: ["#._maycPairs.[]bakcTokenId", "#._recipient"],
      excluded: ["#._maycPairs.[]mainTokenId"],
    };

    const updatedOperation = updateOperationFromSchema(
      operation,
      updatedSchema,
    );

    expect(updatedOperation).toEqual(expectedUpdatedOperation);
  });
});
