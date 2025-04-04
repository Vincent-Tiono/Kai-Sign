import { type UseFormReturn } from "react-hook-form";
import { z } from "zod";
import {
  Form,
  FormControl,
  FormDescription,
  FormField,
  FormItem,
  FormLabel,
} from "~/components/ui/form";
import { type OperationFormType } from "../editOperation";
import { Input } from "~/components/ui/input";

export const TokenAmountFieldFormSchema = z.object({
  tokenPath: z.string().optional(),
  nativeCurrencyAddress: z.union([z.string(), z.array(z.string())]).optional(),
  threshold: z.string().optional(),
  message: z.string().optional().default("Unlimited"),
});

export type TokenAmountFieldFormType = z.infer<
  typeof TokenAmountFieldFormSchema
>;

interface Props {
  form: UseFormReturn<OperationFormType>;
  index: number;
}

const TokenAmountFieldForm = ({ form, index }: Props) => {
  const tokenPathParams = form.watch(
    `fields.${index}.params`,
  ) as TokenAmountFieldFormType;

  return (
    <Form {...form}>
      <FormField
        control={form.control}
        name={`fields.${index}.params.tokenPath`}
        render={({ field }) => (
          <FormItem className="mb-1">
            <FormLabel>Token Path</FormLabel>
            <FormDescription>
              Path reference or constant value for the address of the token
              contract.
            </FormDescription>
            <FormControl>
              <Input
                {...field}
                defaultValue={tokenPathParams?.tokenPath}
                placeholder="Enter token path"
              />
            </FormControl>
          </FormItem>
        )}
      />
      <FormField
        control={form.control}
        name={`fields.${index}.params.nativeCurrencyAddress`}
        render={({ field }) => (
          <FormItem className="mb-1">
            <FormLabel>Native Currency Address</FormLabel>
            <FormDescription>
              Either a single address or an array of addresses. If the token
              path matches one of these addresses, the tokenAmount is
              interpreted as native currency.
            </FormDescription>
            <FormControl>
              <Input
                {...field}
                defaultValue={tokenPathParams?.nativeCurrencyAddress}
                placeholder="Enter native currency address(es)"
              />
            </FormControl>
          </FormItem>
        )}
      />
      <FormField
        control={form.control}
        name={`fields.${index}.params.threshold`}
        render={({ field }) => (
          <FormItem className="mb-1">
            <FormLabel>Threshold</FormLabel>
            <FormDescription>
              Integer value above which a special message is displayed.
              Optional.
            </FormDescription>
            <FormControl>
              <Input
                {...field}
                defaultValue={tokenPathParams?.threshold}
                placeholder="Enter threshold value"
              />
            </FormControl>
          </FormItem>
        )}
      />
      <FormField
        control={form.control}
        name={`fields.${index}.params.message`}
        render={({ field }) => (
          <FormItem className="mb-1">
            <FormLabel>Message</FormLabel>
            <FormDescription>
              Message to display if the value exceeds the threshold. Defaults to
              &quot;Unlimited&quot;.
            </FormDescription>
            <FormControl>
              <Input
                {...field}
                defaultValue={tokenPathParams?.message}
                placeholder="Enter custom message"
              />
            </FormControl>
          </FormItem>
        )}
      />
    </Form>
  );
};

export default TokenAmountFieldForm;

//  chat gpt code to manage multiple addresses in nativeCurrencyAddress
// it can be string or array of strings
// lets try later

{
  /* <FormField
  control={form.control}
  name={`fields.${index}.params.nativeCurrencyAddress`}
  render={({ field }) => {
    const [isArray, setIsArray] = React.useState(
      Array.isArray(tokenPathParams?.nativeCurrencyAddress),
    );
    const [addresses, setAddresses] = React.useState<string[]>(
      Array.isArray(tokenPathParams?.nativeCurrencyAddress)
        ? tokenPathParams?.nativeCurrencyAddress
        : [tokenPathParams?.nativeCurrencyAddress || ""],
    );

    const handleAddInput = () => {
      setAddresses([...addresses, ""]);
    };

    const handleRemoveInput = (index: number) => {
      setAddresses(addresses.filter((_, i) => i !== index));
    };

    const handleInputChange = (value: string, index: number) => {
      const updatedAddresses = [...addresses];
      updatedAddresses[index] = value;
      setAddresses(updatedAddresses);

      // Update the form field value
      field.onChange(updatedAddresses);
    };

    return (
      <FormItem className="mb-1">
        <FormLabel>Native Currency Address</FormLabel>
        <FormDescription>
          Either a single address or an array of addresses. If the token path
          matches one of these addresses, the token amount is interpreted as
          native currency.
        </FormDescription>

        <div className="mb-4 flex items-center gap-2">
          <FormControl>
            <label className="flex items-center">
              <input
                type="checkbox"
                checked={isArray}
                onChange={(e) => {
                  setIsArray(e.target.checked);
                  // Switch between single input or array
                  if (!e.target.checked) {
                    field.onChange(addresses[0] || ""); // Set single input value
                  } else {
                    field.onChange(addresses); // Set array of addresses
                  }
                }}
              />
              <span className="ml-2">Multiple Addresses</span>
            </label>
          </FormControl>
        </div>

        {isArray ? (
          <>
            {addresses.map((address, idx) => (
              <div key={idx} className="mb-2 flex items-center gap-2">
                <Input
                  value={address}
                  onChange={(e) => handleInputChange(e.target.value, idx)}
                  placeholder={`Enter address ${idx + 1}`}
                />
                <button
                  type="button"
                  onClick={() => handleRemoveInput(idx)}
                  className="text-red-500"
                >
                  Remove
                </button>
              </div>
            ))}
            <button
              type="button"
              onClick={handleAddInput}
              className="text-blue-500"
            >
              Add Address
            </button>
          </>
        ) : (
          <FormControl>
            <Input
              {...field}
              value={addresses[0]}
              onChange={(e) => {
                const value = e.target.value;
                setAddresses([value]);
                field.onChange(value); // Update form value
              }}
              placeholder="Enter native currency address"
            />
          </FormControl>
        )}
      </FormItem>
    );
  }}
/>; */
}
