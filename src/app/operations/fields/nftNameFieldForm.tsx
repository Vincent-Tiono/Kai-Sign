import { z } from "zod";
import { Tabs, TabsList, TabsTrigger, TabsContent } from "~/components/ui/tabs";
import {
  Form,
  FormControl,
  FormDescription,
  FormField,
  FormItem,
  FormLabel,
} from "~/components/ui/form";
import { Input } from "~/components/ui/input";
import { type UseFormReturn } from "react-hook-form";
import { type OperationFormType } from "../editOperation";

export const NftNameParametersFormSchema = z
  .object({
    collection: z.string().optional(),
    collectionPath: z.string().optional(),
  })
  .refine((data) => data.collection ?? data.collectionPath, {
    message: "Either 'Collection' or 'Collection Path' must be provided.",
  });

interface Props {
  form: UseFormReturn<OperationFormType>;
  index: number;
}

const NftNameParametersForm = ({ form, index }: Props) => {
  return (
    <>
      <Form {...form}>
        <Tabs>
          <TabsList>
            <TabsTrigger value="collection">Collection Address</TabsTrigger>
            <TabsTrigger value="collectionPath">Collection Path</TabsTrigger>
          </TabsList>

          <TabsContent value="collection">
            <FormField
              control={form.control}
              name={`fields.${index}.params.collection`}
              render={({ field, fieldState }) => (
                <FormItem className="mb-4">
                  <FormLabel>Collection Address</FormLabel>
                  <FormDescription>
                    The collection address, or a path to a constant in the ERC
                    7730 file.
                  </FormDescription>
                  <FormControl>
                    <Input {...field} placeholder="Enter collection address" />
                  </FormControl>
                  {fieldState.error && (
                    <p className="mt-1 text-sm text-red-500">
                      {fieldState.error.message}
                    </p>
                  )}
                </FormItem>
              )}
            />
          </TabsContent>

          <TabsContent value="collectionPath">
            <FormField
              control={form.control}
              name={`fields.${index}.params.collectionPath`}
              render={({ field, fieldState }) => (
                <FormItem className="mb-4">
                  <FormLabel>Collection Path</FormLabel>
                  <FormDescription>
                    The path to the collection in the structured data.
                  </FormDescription>
                  <FormControl>
                    <Input {...field} placeholder="Enter collection path" />
                  </FormControl>
                  {fieldState.error && (
                    <p className="mt-1 text-sm text-red-500">
                      {fieldState.error.message}
                    </p>
                  )}
                </FormItem>
              )}
            />
          </TabsContent>
        </Tabs>
      </Form>
    </>
  );
};

export default NftNameParametersForm;
