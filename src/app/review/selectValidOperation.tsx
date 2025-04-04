"use client";

import { useEffect } from "react";
import {
  Select,
  SelectContent,
  SelectItem,
  SelectTrigger,
  SelectValue,
} from "~/components/ui/select";

import { useErc7730Store } from "~/store/erc7730Provider";
import useOperationStore from "~/store/useOperationStore";

const SelectValidOperation = () => {
  const operation = useErc7730Store((s) => s.getOperations)();
  const { selectedOperation, setSelectedOperation, validateOperation } =
    useOperationStore();

  useEffect(() => {
    void useOperationStore.persist.rehydrate();
  }, []);

  useEffect(() => {
    if (
      !validateOperation.includes(selectedOperation ?? "") &&
      validateOperation.length > 0
    ) {
      setSelectedOperation(validateOperation[0] ?? "");
    }
  }, [selectedOperation, setSelectedOperation, validateOperation]);

  if (!operation?.formats) return null;

  return (
    <Select
      value={selectedOperation ?? ""}
      onValueChange={setSelectedOperation}
    >
      <SelectTrigger className="w-full">
        <SelectValue placeholder="Select an operation" />
      </SelectTrigger>
      <SelectContent>
        {Object.entries(operation.formats)
          .filter(([operationName]) =>
            validateOperation.includes(operationName),
          )
          .map(([operationName]) => (
            <SelectItem key={operationName} value={operationName}>
              {operationName}
            </SelectItem>
          ))}
      </SelectContent>
    </Select>
  );
};

export default SelectValidOperation;
