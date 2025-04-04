import { type paths } from "~/generate/api-types";

type GenerateBody =
  paths["/api/py/generateERC7730"]["post"]["requestBody"]["content"]["application/json"];
export type GenerateResponse =
  paths["/api/py/generateERC7730"]["post"]["responses"]["200"]["content"]["application/json"];

export default async function generateERC7730({
  input,
  inputType,
}: {
  inputType: "address" | "abi";
  input: string;
}): Promise<GenerateResponse | null> {
  const body: GenerateBody = {
    address: inputType === "address" ? input : undefined,
    abi: inputType === "abi" ? input : undefined,
  };

  const response = await fetch("/api/py/generateERC7730", {
    method: "POST",
    headers: {
      "Content-Type": "application/json",
    },
    body: JSON.stringify(body),
  });

  if (!response.ok) {
    const data = (await response.json()) as {
      message: string;
    };
    throw new Error(`API Error: ${data.message}`);
  }

  const data = (await response.json()) as GenerateResponse;

  return data;
}
