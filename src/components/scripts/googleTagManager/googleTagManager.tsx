"use client";
import { useEffect } from "react";
import TagManager from "react-gtm-module";

export interface Props {
  id: string;
}
const GoogleTagManager = ({ id }: Props) => {
  useEffect(() => {
    // eslint-disable-next-line @typescript-eslint/no-unsafe-call, @typescript-eslint/no-unsafe-member-access
    TagManager.initialize({ gtmId: id });
  }, [id]);
  return null;
};
export default GoogleTagManager;
