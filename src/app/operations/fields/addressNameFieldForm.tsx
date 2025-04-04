import { z } from "zod";
import {
  Form,
  FormDescription,
  FormField,
  FormItem,
  FormLabel,
} from "~/components/ui/form";
import { ToggleGroup, ToggleGroupItem } from "~/components/ui/toggle-group";
import { type UseFormReturn } from "react-hook-form";
import { type OperationFormType } from "../editOperation";

// Define schema
export const AddressNameParametersFormSchema = z.object({
  types: z
    .array(z.enum(["wallet", "eoa", "contract", "token", "collection"]))
    .nonempty("At least one address type must be selected."),
  sources: z.array(z.string()),
});

interface Props {
  form: UseFormReturn<OperationFormType>;
  index: number;
}

const AddressNameParametersForm = ({ form, index }: Props) => {
  const addressTypes = [
    {
      value: "wallet",
      description: "Address is an account controlled by the wallet",
    },
    { value: "eoa", description: "Address is an Externally Owned Account" },
    {
      value: "contract",
      description: "Address is a well-known smart contract",
    },
    { value: "token", description: "Address is a well-known ERC-20 token" },
    {
      value: "collection",
      description: "Address is a well-known NFT collection",
    },
  ];

  const addressSources = [
    {
      value: "local",
      description:
        "Address may be replaced with a local name trusted by user. Wallets may consider that local setting for sources is always valid",
    },
    {
      value: "ens",
      description: "Address may be replaced with an associated ENS domain",
    },
  ];

  return (
    <Form {...form}>
      <FormField
        control={form.control}
        name={`fields.${index}.params.types`}
        render={({ field }) => (
          <FormItem className="mb-4">
            <FormLabel>Address Type</FormLabel>
            <FormDescription>
              Select the types of addresses to display. This restricts allowable
              sources of names and may lead to additional checks from wallets.
            </FormDescription>
            <ToggleGroup
              type="multiple"
              className="mt-2 flex flex-wrap justify-start gap-2"
              value={field.value || []}
              onValueChange={(value) => field.onChange(value)}
            >
              {addressTypes.map(({ value }) => (
                <ToggleGroupItem
                  key={value}
                  value={value}
                  className="px-4 py-2 text-sm"
                >
                  {value}
                </ToggleGroupItem>
              ))}
            </ToggleGroup>
            {field.value?.length > 0 && (
              <ul className="mt-2 text-sm text-gray-500">
                {field.value.map((type) => (
                  <li key={type}>
                    <strong>{type}:</strong>{" "}
                    {
                      addressTypes.find((item) => item.value === type)
                        ?.description
                    }
                  </li>
                ))}
              </ul>
            )}
          </FormItem>
        )}
      />

      {/* Trusted Sources Field */}
      <FormField
        control={form.control}
        name={`fields.${index}.params.sources`}
        render={({ field }) => (
          <FormItem className="mb-4">
            <FormLabel>Sources</FormLabel>
            <FormDescription>
              Sources values are wallet manufacturer specific.
            </FormDescription>
            <ToggleGroup
              type="multiple"
              className="mt-2 flex flex-wrap justify-start gap-2"
              value={field.value || []}
              onValueChange={(value) => field.onChange(value)}
            >
              {addressSources.map(({ value }) => (
                <ToggleGroupItem
                  key={value}
                  value={value}
                  className="px-4 py-2 text-sm"
                >
                  {value}
                </ToggleGroupItem>
              ))}
            </ToggleGroup>
            {field.value?.length > 0 && (
              <ul className="mt-2 text-sm text-gray-500">
                {field.value.map((type) => (
                  <li key={type}>
                    <strong>{type}:</strong>{" "}
                    {
                      addressSources.find((item) => item.value === type)
                        ?.description
                    }
                  </li>
                ))}
              </ul>
            )}
          </FormItem>
        )}
      />
    </Form>
  );
};

export default AddressNameParametersForm;
