import { cn } from "~/lib/utils";
import { Device } from "./device";
import { type DisplayItem } from "~/shared/getScreensForOperation";

export const ReviewScreen = ({ screen }: { screen: DisplayItem[] }) => {
  const isStax = true;

  return (
    <div
      className={cn(
        "flex flex-col items-start",
        isStax ? "mt-4 gap-[6px] p-3" : "mt-5 gap-3 px-4",
      )}
    >
      {screen
        .filter((t) => t)
        .map(({ label, displayValue, isActive }, index) => (
          <div
            key={`${label}-field-${index}`}
            className={cn("text-black/30", isActive && "text-black")}
          >
            <Device.ContentText>
              <span>{label}</span>
            </Device.ContentText>
            <Device.HeadingText>{displayValue}</Device.HeadingText>
          </div>
        ))}
    </div>
  );
};
