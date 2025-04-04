import { type Operation } from "~/store/types";
import { type OperationFormType } from "~/app/operations/editOperation";

export function updateOperationFromSchema(
  operation: Operation,
  updatedSchema: OperationFormType,
): Operation {
  const updatedFields = new Map<string, OperationFormType["fields"][number]>();
  const excludedPaths: string[] = [];
  const requiredPaths: string[] = [];

  updatedSchema.fields.forEach((field) => {
    updatedFields.set(field.path, field);
    if (!field.isIncluded) {
      excludedPaths.push(field.path);
    }
    if (field.isRequired) {
      requiredPaths.push(field.path);
    }
  });

  function traverseAndUpdateFields(
    fieldsArray: Operation["fields"],
    parentPath = "",
  ) {
    fieldsArray.forEach((field) => {
      const fullPath = `${parentPath}${field.path}`;
      if ("fields" in field && field.fields.length > 0) {
        traverseAndUpdateFields(field.fields, fullPath);
      } else {
        const updatedField = updatedFields.get(fullPath);
        if (updatedField) {
          if ("label" in field && "label" in updatedField) {
            field.label = updatedField.label;
          }
          if ("format" in field && "format" in updatedField) {
            field.format = updatedField.format;
          }
          if ("params" in field && "params" in updatedField) {
            field.params = updatedField.params;
          }
        }
      }
    });
  }

  traverseAndUpdateFields(operation.fields);

  // Filter out any required paths that are also in the excluded paths
  const filteredRequiredPaths = requiredPaths.filter(
    (path) => !excludedPaths.includes(path),
  );

  console.log("filteredRequiredPaths", {
    ...operation,
    intent: updatedSchema.intent,
    fields: operation.fields,
    excluded: excludedPaths.length > 0 ? excludedPaths : null,
    required: filteredRequiredPaths.length > 0 ? filteredRequiredPaths : null,
  });

  return {
    ...operation,
    intent: updatedSchema.intent,
    fields: operation.fields,
    excluded: excludedPaths.length > 0 ? excludedPaths : null,
    required: filteredRequiredPaths.length > 0 ? filteredRequiredPaths : null,
  };
}
