import { type OperationFormType } from "~/app/operations/editOperation";
import matchFieldFormatToMockData from "~/lib/matchFormatToMockData";
import { type Operation } from "~/store/types";

const ITEM_PER_SCREEN = 4;
export interface DisplayItem {
  label: string;
  isActive?: boolean;
  displayValue: string;
}

export type Screen = DisplayItem[];

export const getScreensForOperation = (
  operation: Operation,
  activeFieldPath?: string,
) => {
  const displays = operation.fields.filter((field) => {
    const label = field && "label" in field ? field.label : undefined;

    return !(label === undefined || label === null || label === "");
  });

  const itemsPerScreen = ITEM_PER_SCREEN;

  const screens: Screen[] = [];
  let screen: DisplayItem[] = [];

  for (let i = 0; i < displays.length; i++) {
    const isLastItem = i === displays.length - 1;

    const displayItem = displays[i];
    const label =
      displayItem && "label" in displayItem ? displayItem.label : undefined;

    if (label === undefined || label === null || label === "") continue;
    if (!displayItem) continue;

    screen.push({
      label,
      isActive:
        activeFieldPath === displayItem.path || activeFieldPath === undefined,
      displayValue:
        "format" in displayItem
          ? matchFieldFormatToMockData(
              displayItem?.format ?? "",
              displayItem.params,
            )
          : "displayValue",
    });

    if (screen.length === itemsPerScreen || isLastItem) {
      screens.push(screen);
      screen = [];
    }
  }

  return screens;
};

export const getScreensForForm = (
  formFields: OperationFormType["fields"],
  activeFieldPath: string,
): Screen[] => {
  const screens: Screen[] = [];

  let screen: DisplayItem[] = [];

  formFields.forEach((field, index) => {
    if (field.isIncluded) {
      screen.push({
        label: field.label,
        isActive: activeFieldPath === field.path,
        displayValue: matchFieldFormatToMockData(
          field.format ?? "raw",
          field.params,
        ),
      });
    }

    if (screen.length === ITEM_PER_SCREEN || index === formFields.length - 1) {
      screens.push(screen);
      screen = [];
    }
  });

  return screens;
};
