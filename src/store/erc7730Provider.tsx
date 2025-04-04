"use client";

import {
  createContext,
  useRef,
  useContext,
  type ReactNode,
  useEffect,
} from "react";
import createStore, { type Erc7730Store } from "./erc7730Store";
import { useStore } from "zustand";

export type Erc7730StoreApi = ReturnType<typeof createStore>;

export const Erc7730StoreContext = createContext<Erc7730StoreApi | undefined>(
  undefined,
);

export interface Erc7730StoreProviderProps {
  children: ReactNode;
}

export const Erc7730StoreProvider = ({
  children,
}: Erc7730StoreProviderProps) => {
  const storeRef = useRef<Erc7730StoreApi>();
  if (!storeRef.current) {
    storeRef.current = createStore();
  }

  return (
    <Erc7730StoreContext.Provider value={storeRef.current}>
      {children}
    </Erc7730StoreContext.Provider>
  );
};

export const useErc7730Store = <T,>(
  selector: (store: Erc7730Store) => T,
): T => {
  const erc7730StoreContext = useContext(Erc7730StoreContext);

  useEffect(() => {
    void erc7730StoreContext?.persist?.rehydrate();
  }, [erc7730StoreContext]);

  if (!erc7730StoreContext) {
    throw new Error(`useErc7730Store must be used within erc7730StoreProvider`);
  }

  return useStore(erc7730StoreContext, selector);
};
