import "~/styles/globals.css";

import { GeistSans } from "geist/font/sans";
import { type Metadata } from "next";
import { env } from "~/env.js";
import { TRPCReactProvider } from "~/trpc/react";
import { Erc7730StoreProvider } from "~/store/erc7730Provider";
import { Toaster } from "~/components/ui/toaster";
import { ThemeProvider } from "~/components/ui/theme-provider";
import GoogleTagManager from "~/components/scripts/googleTagManager";
import Script from "next/script";

export const metadata: Metadata = {
  title: "Create Erc7730 Json",
  description: "Clear sign all the things",
  icons: [{ rel: "icon", url: "/ledger-logo-short-black.svg" }],
  openGraph: {
    title: "Create Erc7730 Json",
    description: "Clear sign all the things",
    images: [
      {
        url: "/openGraphImage.png",
        width: 1200,
        height: 630,
      },
    ],
    type: "website",
  },
};

const GTM_ID = env.NEXT_PUBLIC_GTM;
const ONETRUST_ID = env.NEXT_PUBLIC_ONETRUST;
const ONETRUST_ENVIROMENT_ID =
  env.NODE_ENV === "production" ? ONETRUST_ID : `${ONETRUST_ID}-test`;

export default function RootLayout({
  children,
}: Readonly<{ children: React.ReactNode }>) {
  return (
    <html
      lang="en"
      className={`${GeistSans.variable}`}
      suppressHydrationWarning
    >
      <body>
        <TRPCReactProvider>
          <Erc7730StoreProvider>
            <ThemeProvider
              attribute="class"
              defaultTheme="system"
              enableSystem
              disableTransitionOnChange
            >
              {children}
              <Toaster />
            </ThemeProvider>
          </Erc7730StoreProvider>
        </TRPCReactProvider>
        {ONETRUST_ID && (
          <Script
            strategy="beforeInteractive"
            src="https://cdn.cookielaw.org/scripttemplates/otSDKStub.js"
            data-domain-script={`${ONETRUST_ENVIROMENT_ID}`}
            data-document-language="true"
            data-testid="one-trust-script-sdk"
          />
        )}
        {GTM_ID && <GoogleTagManager id={GTM_ID} />}
      </body>
    </html>
  );
}
