import { type OperationFormType } from "~/app/operations/editOperation";
import { type Operation } from "~/store/types";

export function convertOperationToSchema(operation: Operation) {
  const fields: OperationFormType["fields"] = [];

  function traverseFields(fieldsArray: Operation["fields"], parentPath = "") {
    fieldsArray.forEach((field) => {
      const fullPath = `${parentPath}${field.path}`;
      if ("fields" in field && field.fields.length > 0) {
        traverseFields(field.fields, fullPath);
      } else {
        fields.push({
          label: "label" in field ? (field.label ?? "") : "",
          format: "format" in field ? (field.format ?? "raw") : "raw",
          params: "params" in field ? (field.params ?? null) : null,
          path: fullPath,
          isRequired: operation.required
            ? operation.required.includes(fullPath)
            : !operation.excluded?.includes(fullPath),
          isIncluded: operation.excluded
            ? !operation.excluded.includes(fullPath)
            : true,
        });
      }
    });
  }

  traverseFields(operation.fields);

  return {
    intent: typeof operation.intent === "string" ? operation.intent : "",
    fields,
  };
}
