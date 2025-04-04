import { z } from "zod";
import {
  Form,
  FormControl,
  FormDescription,
  FormField,
  FormItem,
  FormLabel,
} from "~/components/ui/form";
import { Input } from "~/components/ui/input";
import { Button } from "~/components/ui/button";
import { type UseFormReturn } from "react-hook-form";
import { type OperationFormType } from "../editOperation";

// Schema updated to match expected types
export const UnitParametersFormSchema = z.object({
  base: z.string({ required_error: "Base unit symbol is required" }), // base as string
  decimals: z
    .string()
    .regex(/^\d*$/, "Decimals must be an integer.") // enforce as string with integer validation
    .optional(),
  prefix: z.string().optional(),
});

interface Props {
  form: UseFormReturn<OperationFormType>;
  index: number;
}

const UnitParametersForm = ({ form, index }: Props) => {
  // to check
  return (
    <Form {...form}>
      <div>Test every thing</div>
      {/* Base Unit Symbol */}
      <FormField
        control={form.control}
        name={`fields.${index}.params.base`}
        render={({ field }) => (
          <FormItem className="mb-4">
            <FormLabel>Unit Base Symbol</FormLabel>
            <FormDescription>
              The base symbol of the unit, displayed after the converted value.
              It can be an SI unit symbol or acceptable dimensionless symbols
              like % or bps.
            </FormDescription>
            <FormControl>
              <Input placeholder="Enter base unit (e.g., %, bps)" {...field} />
            </FormControl>
          </FormItem>
        )}
      />

      {/* Decimals */}
      <FormField
        control={form.control}
        name={`fields.${index}.params.decimals`}
        render={({ field }) => (
          <FormItem className="mb-4">
            <FormLabel>Decimals</FormLabel>
            <FormDescription>
              The number of decimals of the value, used to convert to a float.
            </FormDescription>
            <FormControl>
              <Input placeholder="Enter number of decimals" {...field} />
            </FormControl>
          </FormItem>
        )}
      />

      {/* Prefix */}
      <FormField
        control={form.control}
        name={`fields.${index}.params.prefix`}
        render={({ field }) => (
          <FormItem className="f mb-">
            <FormLabel>Prefix</FormLabel>
            <FormControl>
              <Input placeholder="Enter a prefix" {...field} />
            </FormControl>
            <FormDescription>
              Whether the value should be converted to a prefixed unit, like k,
              M, G, etc.
            </FormDescription>
          </FormItem>
        )}
      />

      {/* Save Button */}
      <Button type="submit">Save</Button>
    </Form>
  );
};

export default UnitParametersForm;
