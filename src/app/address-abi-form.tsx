"use client";

import { Input } from "~/components/ui/input";
import { Card, CardContent, CardHeader, CardTitle } from "~/components/ui/card";
import { Label } from "~/components/ui/label";

import { useState } from "react";
import { Textarea } from "~/components/ui/textarea";
import { Tabs, TabsContent, TabsList, TabsTrigger } from "~/components/ui/tabs";
import SampleAddressAbiCard from "./sampleAddressAbiCard";
import { Button } from "~/components/ui/button";
import { FileJson } from "lucide-react";

import { ZodError } from "zod";
import { useMutation } from "@tanstack/react-query";
import { useRouter } from "next/navigation";
import { useErc7730Store } from "~/store/erc7730Provider";
import useFunctionStore from "~/store/useOperationStore";
import generateFromERC7730 from "./generateFromERC7730";

const CardErc7730 = () => {
  const [input, setInput] = useState("");
  const [inputType, setInputType] = useState<"address" | "abi">("address");
  const { setErc7730 } = useErc7730Store((state) => state);
  const router = useRouter();

  const {
    mutateAsync: fetchERC7730Metadata,
    isPending: loading,
    error,
  } = useMutation({
    mutationFn: (input: string) =>
      generateFromERC7730({
        input,
        inputType,
      }),
  });

  const handleSubmit = async (e: React.FormEvent) => {
    e.preventDefault();
    const erc7730 = await fetchERC7730Metadata(input);

    if (erc7730) {
      console.log(erc7730);
      useFunctionStore.persist.clearStorage();

      setErc7730(erc7730);
      router.push("/metadata");
    }
  };

  const onTabChange = (value: string) => {
    setInputType(value as "address" | "abi");
    setInput("");
  };
  
  const handleSkipToVerification = () => {
    router.push("/verification-results");
  };

  return (
    <div className="w-full lg:w-[580px]">
      <form onSubmit={handleSubmit} className="mb-4 flex w-full flex-col gap-4">
        <Tabs defaultValue="address" onValueChange={onTabChange}>
          <TabsList className="mb-10 grid w-full grid-cols-2">
            <TabsTrigger value="address">Contract Address</TabsTrigger>
            <TabsTrigger value="abi">ABI</TabsTrigger>
          </TabsList>
          <TabsContent value="address">
            <div className="space-y-4">
              <div className="space-y-2">
                <Label htmlFor="eth-address">Contract Address</Label>
                <Input
                  id="contract-address"
                  placeholder="0x..."
                  value={input}
                  onChange={(e) => setInput(e.target.value)}
                />
              </div>
            </div>
          </TabsContent>
          <TabsContent value="abi">
            <div className="space-y-4">
              <div className="space-y-2">
                <Label htmlFor="abi">ABI</Label>
                <Textarea
                  id="abi"
                  placeholder="Paste your ABI here..."
                  value={input}
                  onChange={(e) => setInput(e.target.value)}
                />
              </div>
            </div>
          </TabsContent>
        </Tabs>
        <div className="flex justify-between gap-4">
          <Button type="submit" disabled={loading}>
            Submit
          </Button>
          <Button 
            type="button" 
            variant="outline" 
            onClick={handleSkipToVerification}
          >
            <FileJson className="mr-2 h-4 w-4" />
            I already have a JSON file
          </Button>
        </div>
      </form>

      <SampleAddressAbiCard setInput={setInput} inputType={inputType} />

      {error && (
        <Card>
          <CardHeader>
            <CardTitle>Error</CardTitle>
          </CardHeader>
          <CardContent>
            {error instanceof ZodError
              ? // eslint-disable-next-line @typescript-eslint/no-unsafe-member-access
                JSON.parse(error.message)[0].message
              : error.message}
          </CardContent>
        </Card>
      )}
    </div>
  );
};

export default CardErc7730;
