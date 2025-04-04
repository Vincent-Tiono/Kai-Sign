import { describe, it, expect } from "vitest";
import { removeExcludedFields } from "./removeExcludedFields";
import { type Operation } from "~/store/types";

describe("removeExcludedFields", () => {
  it("should remove fields where the path is in the excluded array", () => {
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
                  label: "Main Token Id",
                  format: "raw",
                  params: {},
                  path: "mainTokenId",
                  value: null,
                },
                {
                  $id: null,
                  label: "Bakc Token Id",
                  format: "raw",
                  params: {},
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
                  params: {},
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
      required: null,
      excluded: ["#._maycPairs.[]mainTokenId"],
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
                  params: {},
                  path: "mainTokenId",
                  value: null,
                },
                {
                  $id: null,
                  label: "Bakc Token Id",
                  format: "raw",
                  params: {},
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
                  label: "Bakc Token Id",
                  format: "raw",
                  params: {},
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
      required: null,
      excluded: ["#._maycPairs.[]mainTokenId"],
    };

    const updatedOperation = removeExcludedFields(operation);

    expect(updatedOperation).toEqual(expectedUpdatedOperation);
  });
});
