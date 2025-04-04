import { type UseFormReturn } from "react-hook-form";
import { type OperationFormType } from "../editOperation";
import DateFieldForm from "./dateFieldForm";
import { type Operation } from "~/store/types";
import RawFieldForm from "./rawFieldForm";
import CallDataFieldForm from "./callDataFieldForm";
import AmountFieldForm from "./amountFieldForm";
import { FormField, FormItem, FormLabel } from "~/components/ui/form";
import {
  Select,
  SelectContent,
  SelectItem,
  SelectTrigger,
  SelectValue,
} from "~/components/ui/select";
import { type components } from "~/generate/api-types";
import TokenAmountFieldForm from "./tokenAmountFormField";
import NftNameParametersForm from "./nftNameFieldForm";
import AddressNameParametersForm from "./addressNameFieldForm";
import DurationFieldForm from "./durationFieldForm";
import UnitParametersForm from "./unitFieldForm";

interface Props {
  form: UseFormReturn<OperationFormType>;
  index: number;
  field: Operation["fields"][number];
}

const FieldOption = ({ form, index, field }: Props) => {
  const format = form.watch(`fields.${index}.format`) as string;

  if (!("format" in field)) return <div>unknown field format</div>;

  if (format === "raw") {
    return <RawFieldForm />;
  }

  if (format === "amount") {
    return <AmountFieldForm />;
  }

  if (format === "tokenAmount") {
    return <TokenAmountFieldForm form={form} index={index} />;
  }

  if (format === "addressName") {
    return <AddressNameParametersForm form={form} index={index} />;
  }

  if (format === "calldata") {
    return <CallDataFieldForm />;
  }

  if (format === "nftName") {
    return <NftNameParametersForm form={form} index={index} />;
  }

  if (format === "date") {
    return <DateFieldForm form={form} index={index} />;
  }

  if (format === "duration") {
    return <DurationFieldForm />;
  }

  if (format === "unit") {
    return <UnitParametersForm form={form} index={index} />;
  }

  return <div>{format}</div>;
};

const possibleFormats: components["schemas"]["FieldFormat"][] = [
  "raw",
  "amount",
  "tokenAmount",
  "addressName",
  "calldata",
  "nftName",
  "date",
  "duration",
  "unit",
  // "enum",
];

const FieldSelector = ({ form, index, field }: Props) => {
  return (
    <div className="flex flex-col gap-2">
      <FormField
        control={form.control}
        name={`fields.${index}.format`}
        render={({ field }) => (
          <FormItem>
            <FormLabel className="mt-1">Field format</FormLabel>
            <Select
              onValueChange={(value) => {
                form.setValue(`fields.${index}.params`, null);
                field.onChange(value);
              }}
              defaultValue={field.value as string | undefined}
            >
              <SelectTrigger className="h-8 w-full text-sm">
                <SelectValue placeholder="value" />
              </SelectTrigger>
              <SelectContent>
                {possibleFormats.map((format) => (
                  <SelectItem key={format} value={format}>
                    {format}
                  </SelectItem>
                ))}
              </SelectContent>
            </Select>
          </FormItem>
        )}
      />
      <FieldOption form={form} index={index} field={field} />
    </div>
  );
};

export default FieldSelector;
