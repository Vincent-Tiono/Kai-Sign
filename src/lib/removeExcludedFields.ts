import { type Operation } from "~/store/types";

export function removeExcludedFields(operation: Operation): Operation {
  function traverseAndRemoveFields(
    fieldsArray: Operation["fields"],
    excludedPaths: string[],
    parentPath = "",
  ): Operation["fields"] {
    return fieldsArray.filter((field) => {
      const fullPath = `${parentPath}${field.path}`;
      if (excludedPaths.includes(fullPath)) {
        return false;
      }
      if ("fields" in field && field.fields.length > 0) {
        field.fields = traverseAndRemoveFields(
          field.fields,
          excludedPaths,
          fullPath,
        );
      }
      return true;
    });
  }

  const excludedPaths = operation.excluded ?? [];
  const updatedFields = traverseAndRemoveFields(
    operation.fields,
    excludedPaths,
  );

  return {
    ...operation,
    fields: updatedFields,
  };
}
