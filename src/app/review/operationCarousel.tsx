"use client";

import * as React from "react";

import { useEffect, useState } from "react";
import {
  type CarouselApi,
  Carousel,
  CarouselContent,
  CarouselItem,
  CarouselNext,
  CarouselPrevious,
} from "~/components/ui/carousel";
import { cn } from "~/lib/utils";
import useOperationStore from "~/store/useOperationStore";
import { useErc7730Store } from "~/store/erc7730Provider";
import { getScreensForOperation } from "~/shared/getScreensForOperation";
import { Device } from "~/components/devices/device";
import operationScreens from "./operationScreens";

const OperationCarousel = () => {
  const [api, setApi] = useState<CarouselApi>();
  const [, setCount] = useState(0);
  const [selected, setSelected] = useState(0);
  const { selectedOperation } = useOperationStore();
  const operation = useErc7730Store((s) => s.getFinalOperationByName)(
    selectedOperation,
  );

  const operationMetadata = useErc7730Store((s) => s.getOperationsMetadata)(
    selectedOperation,
  );

  useEffect(() => {
    if (!api) {
      return;
    }

    setCount(api.scrollSnapList().length);
    setSelected(api.selectedScrollSnap());

    api.on("select", () => {
      setSelected(api.selectedScrollSnap());
    });
  }, [api]);

  if (!operation || !operationMetadata) return null;

  if (operation.intent === "" || operation.intent === null) {
    return <div>Transaction is not clear sign</div>;
  }
  const screens = getScreensForOperation(operation);
  const fullOperationScreens = operationScreens(screens, operationMetadata);

  return (
    <div className="mx-auto flex max-w-96 flex-col">
      <Carousel setApi={setApi}>
        <CarouselContent>
          {fullOperationScreens.map((screen, index) => (
            <CarouselItem
              key={index}
              className="flex w-full items-center justify-center"
            >
              <Device.Frame>{screen}</Device.Frame>
            </CarouselItem>
          ))}
        </CarouselContent>
        <CarouselPrevious className="hidden md:flex" />
        <CarouselNext className="hidden md:flex" />
      </Carousel>
      <div className="mx-auto flex flex-row items-center gap-4 p-2">
        {fullOperationScreens.map((_, index) => (
          <div
            key={"carrousel-thumbnail-" + index}
            className={cn("w-fit rounded p-1 ring-primary hover:ring-2", {
              "ring-2": index === selected,
            })}
            onClick={() => api?.scrollTo(index)}
          >
            <Device.Frame size="small">{index + 1}</Device.Frame>
          </div>
        ))}
      </div>
    </div>
  );
};

export default OperationCarousel;
