"use client";

import { useRouter } from "next/navigation";
import { useContext, useEffect } from "react";
import { useForm } from "react-hook-form";
import { z } from "zod";
import { zodResolver } from "@hookform/resolvers/zod";
import {
  Form,
  FormControl,
  FormDescription,
  FormField,
  FormItem,
  FormLabel,
  FormMessage,
} from "~/components/ui/form";
import { Input } from "~/components/ui/input";
import { Button } from "~/components/ui/button";
import Devices from "./devices";
import { Erc7730StoreContext, useErc7730Store } from "~/store/erc7730Provider";
import { Card } from "~/components/ui/card";

const metaDataSchema = z.object({
  owner: z.string().min(1, {
    message: "Contract owner name is required.",
  }),
  url: z.string().min(1, {
    message: "URL is required.",
  }),
  legalName: z.string().min(1, {
    message: "Legal name is required.",
  }),
});

type MetadataFormType = z.infer<typeof metaDataSchema>;

const MetadataForm = () => {
  const router = useRouter();
  const hasHydrated = useContext(Erc7730StoreContext)?.persist?.hasHydrated();

  const { getMetadata, setMetadata, getContractAddress } = useErc7730Store(
    (s) => s,
  );
  const metadata = getMetadata();
  const address = getContractAddress();

  const form = useForm<MetadataFormType>({
    resolver: zodResolver(metaDataSchema),
    values: {
      owner: metadata?.owner ?? "",
      url: metadata?.info?.url ?? "",
      legalName: metadata?.info?.legalName ?? "",
    },
  });

  form.watch((value) => {
    if (hasHydrated === false) return;
    setMetadata({
      owner: value.owner,
      info: {
        legalName: value.legalName ?? "",
        url: value.url ?? "",
      },
    });
  });

  useEffect(() => {
    if (hasHydrated && metadata === null) {
      router.push("/");
    }
  }, [metadata, router, hasHydrated, form]);

  const onSubmit = (data: MetadataFormType) => {
    setMetadata({
      owner: data.owner,
      info: {
        legalName: data.legalName,
        url: data.url,
      },
    });
    router.push("/operations");
  };

  if (hasHydrated !== true) {
    return <div>Loading...</div>;
  }

  return (
    <>
      <div className="mb-20 flex w-full items-center justify-between">
        <h1 className="text-2xl font-bold">Metadata</h1>
      </div>
      <Form {...form}>
        <form
          onSubmit={form.handleSubmit(onSubmit)}
          className="grid grid-cols-2 gap-10"
        >
          <div>
            <Card className="mb-40 flex h-fit flex-col gap-6 p-6">
              <FormField
                control={form.control}
                name="owner"
                render={({ field }) => (
                  <FormItem>
                    <FormLabel>Contract owner name</FormLabel>
                    <FormControl>
                      <Input {...field} />
                    </FormControl>
                    <FormMessage />
                  </FormItem>
                )}
              />
              <FormField
                control={form.control}
                name="legalName"
                render={({ field }) => (
                  <FormItem>
                    <FormLabel>Legal Name</FormLabel>
                    <FormControl>
                      <Input {...field} />
                    </FormControl>
                    <FormMessage />
                  </FormItem>
                )}
              />
              <FormField
                control={form.control}
                name="url"
                render={({ field }) => (
                  <FormItem>
                    <div>
                      <FormLabel>URL</FormLabel>
                      <FormDescription>
                        Where to find information on the entity the user
                        interacts with.
                      </FormDescription>
                    </div>
                    <FormControl>
                      <Input {...field} />
                    </FormControl>

                    <FormMessage />
                  </FormItem>
                )}
              />
            </Card>
            <div className="flex w-full items-center justify-end">
              <Button onClick={form.handleSubmit(onSubmit)}>Continue</Button>
            </div>
          </div>
          {metadata && (
            <div className="hidden flex-row justify-between lg:flex">
              <Devices metadata={metadata} address={address} />
            </div>
          )}
        </form>
      </Form>
    </>
  );
};

export default MetadataForm;
