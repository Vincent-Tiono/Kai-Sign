"use client";

import { useErc7730Store } from "~/store/erc7730Provider";
import useOperationStore from "~/store/useOperationStore";

const OperationNotValidated = () => {
  const operation = useErc7730Store((s) => s.getOperations)();
  const { validateOperation } = useOperationStore();

  const numberOfOperations = operation?.formats
    ? Object.keys(operation.formats).length
    : 0;

  const numberOfNotValidatedOperations =
    numberOfOperations - validateOperation.length;
  return <div>{numberOfNotValidatedOperations} operation not clear signed</div>;
};

export default OperationNotValidated;
