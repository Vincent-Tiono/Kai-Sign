import { Button } from "~/components/ui/button";
import {
  Drawer,
  DrawerTrigger,
  DrawerContent,
  DrawerHeader,
  DrawerTitle,
} from "~/components/ui/drawer";

import { type UseFormReturn } from "react-hook-form";
import { Device } from "~/components/devices/device";
import { ReviewScreen } from "~/components/devices/reviewScreen";
import { getScreensForOperation } from "~/shared/getScreensForOperation";
import { type OperationMetadata, type Operation } from "~/store/types";
import { type OperationFormType } from "./editOperation";
import { TitleScreen } from "~/components/devices/titleScreen";

interface Props {
  operation: Operation;
  form: UseFormReturn<OperationFormType>;
  operationMetadata: OperationMetadata | null;
}

const ReviewOperationsButton = ({
  form,
  operation,
  operationMetadata,
}: Props) => {
  const { fields, intent } = form.watch();

  if (fields.length === 0) return null;

  const screens = getScreensForOperation({
    ...operation,
    fields: operation.fields
      .map((field, index) => ({
        ...field,
        ...fields[index],
      }))
      .filter((field) => field.isIncluded),
  });

  const totalPages = screens.length + 1;

  return (
    <div className="w-full lg:hidden">
      <Drawer>
        <DrawerTrigger asChild>
          <Button className="w-full">See on devices</Button>
        </DrawerTrigger>
        <DrawerContent className="h-[80%]">
          <DrawerHeader>
            <DrawerTitle className="sr-only">ledger devices</DrawerTitle>
          </DrawerHeader>
          <div className="overflow-y-auto">
            <div className="flex flex-col items-center justify-center gap-2">
              <Device.Frame>
                <TitleScreen
                  functionName={intent ?? "{functionName}"}
                  type={"transaction"}
                  owner={operationMetadata?.metadata?.owner ?? ""}
                />
                <Device.Pagination current={1} total={1} />
              </Device.Frame>
              {screens.map((screen, index) => (
                <Device.Frame key={`review-screen-${index}`}>
                  <ReviewScreen screen={screen} />
                  <Device.Pagination current={index + 2} total={totalPages} />
                </Device.Frame>
              ))}
            </div>
          </div>
        </DrawerContent>
      </Drawer>
    </div>
  );
};

export default ReviewOperationsButton;
