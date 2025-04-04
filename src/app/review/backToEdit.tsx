"use client";

import { ArrowBigLeft } from "lucide-react";
import { useRouter } from "next/navigation";
import { Button } from "~/components/ui/button";

const BackToEdit = () => {
  const router = useRouter();

  return (
    <Button
      className="w-fit"
      onClick={() => {
        router.push("/operations");
      }}
    >
      Back to edit
    </Button>
  );
};

export default BackToEdit;
