import { type Dispatch, type SetStateAction } from "react";
import {
  Card,
  CardContent,
  CardDescription,
  CardHeader,
  CardTitle,
} from "~/components/ui/card";
import { Button } from "~/components/ui/button";

const predefinedAddresses = [
  {
    label: "Poap",
    value: "0x0bb4D3e88243F4A057Db77341e6916B0e449b158",
  },
  {
    label: "Apecoin: Staking",
    value: "0x5954ab967bc958940b7eb73ee84797dc8a2afbb9",
  },
];

const predefinedABIs = [
  {
    label: "Poap",
    value:
      '[{"inputs":[{"internalType":"address","name":"_poapContractAddress","type":"address"},{"internalType":"address","name":"_validSigner","type":"address"},{"internalType":"address payable","name":"_feeReceiver","type":"address"},{"internalType":"uint256","name":"_migrationFee","type":"uint256"}],"stateMutability":"nonpayable","type":"constructor"},{"anonymous":false,"inputs":[{"indexed":true,"internalType":"address","name":"previousFeeReceiver","type":"address"},{"indexed":true,"internalType":"address","name":"newFeeReceiver","type":"address"}],"name":"FeeReceiverChange","type":"event"},{"anonymous":false,"inputs":[{"indexed":true,"internalType":"uint256","name":"previousFeeReceiver","type":"uint256"},{"indexed":true,"internalType":"uint256","name":"newFeeReceiver","type":"uint256"}],"name":"MigrationFeeChange","type":"event"},{"anonymous":false,"inputs":[{"indexed":true,"internalType":"address","name":"previousOwner","type":"address"},{"indexed":true,"internalType":"address","name":"newOwner","type":"address"}],"name":"OwnershipTransferred","type":"event"},{"anonymous":false,"inputs":[{"indexed":false,"internalType":"address","name":"account","type":"address"}],"name":"Paused","type":"event"},{"anonymous":false,"inputs":[{"indexed":false,"internalType":"address","name":"account","type":"address"}],"name":"Unpaused","type":"event"},{"anonymous":false,"inputs":[{"indexed":true,"internalType":"address","name":"previousValidSigner","type":"address"},{"indexed":true,"internalType":"address","name":"newValidSigner","type":"address"}],"name":"ValidSignerChange","type":"event"},{"anonymous":false,"inputs":[{"indexed":false,"internalType":"bytes","name":"_signature","type":"bytes"}],"name":"VerifiedSignature","type":"event"},{"inputs":[],"name":"NAME","outputs":[{"internalType":"string","name":"","type":"string"}],"stateMutability":"view","type":"function"},{"inputs":[],"name":"feeReceiver","outputs":[{"internalType":"address payable","name":"","type":"address"}],"stateMutability":"view","type":"function"},{"inputs":[],"name":"migrationFee","outputs":[{"internalType":"uint256","name":"","type":"uint256"}],"stateMutability":"view","type":"function"},{"inputs":[{"internalType":"uint256","name":"mockEventId","type":"uint256"},{"internalType":"uint256","name":"tokenId","type":"uint256"},{"internalType":"address","name":"receiver","type":"address"},{"internalType":"uint256","name":"expirationTime","type":"uint256"},{"internalType":"bytes","name":"signature","type":"bytes"}],"name":"mintToken","outputs":[{"internalType":"bool","name":"","type":"bool"}],"stateMutability":"payable","type":"function"},{"inputs":[],"name":"owner","outputs":[{"internalType":"address","name":"","type":"address"}],"stateMutability":"view","type":"function"},{"inputs":[],"name":"pause","outputs":[],"stateMutability":"nonpayable","type":"function"},{"inputs":[],"name":"paused","outputs":[{"internalType":"bool","name":"","type":"bool"}],"stateMutability":"view","type":"function"},{"inputs":[{"internalType":"bytes","name":"","type":"bytes"}],"name":"processed","outputs":[{"internalType":"bool","name":"","type":"bool"}],"stateMutability":"view","type":"function"},{"inputs":[],"name":"renounceOwnership","outputs":[],"stateMutability":"nonpayable","type":"function"},{"inputs":[],"name":"renouncePoapAdmin","outputs":[],"stateMutability":"nonpayable","type":"function"},{"inputs":[{"internalType":"address payable","name":"_feeReceiver","type":"address"}],"name":"setFeeReceiver","outputs":[],"stateMutability":"nonpayable","type":"function"},{"inputs":[{"internalType":"uint256","name":"_migrationFee","type":"uint256"}],"name":"setMigrationFee","outputs":[],"stateMutability":"nonpayable","type":"function"},{"inputs":[{"internalType":"address","name":"_validSigner","type":"address"}],"name":"setValidSigner","outputs":[],"stateMutability":"nonpayable","type":"function"},{"inputs":[{"internalType":"address","name":"newOwner","type":"address"}],"name":"transferOwnership","outputs":[],"stateMutability":"nonpayable","type":"function"},{"inputs":[],"name":"unpause","outputs":[],"stateMutability":"nonpayable","type":"function"},{"inputs":[],"name":"validSigner","outputs":[{"internalType":"address","name":"","type":"address"}],"stateMutability":"view","type":"function"}]',
  },
];

interface Props {
  setInput: Dispatch<SetStateAction<string>>;
  inputType: "address" | "abi";
}

const SampleAddressAbiCard = ({ setInput, inputType }: Props) => {
  const data = inputType === "address" ? predefinedAddresses : predefinedABIs;
  return (
    <Card className="mb-4">
      <CardHeader>
        <CardTitle>
          Sample {inputType === "address" ? "Address" : "ABI"}
        </CardTitle>
        <CardDescription>
          Click to copy a sample {inputType === "address" ? "address" : "ABI"}{" "}
          for testing
        </CardDescription>
      </CardHeader>
      <CardContent>
        <div className="flex flex-wrap gap-2">
          {data.map(({ value, label }) => (
            <Button
              key={value}
              variant="outline"
              onClick={() => {
                void navigator.clipboard.writeText(value);
                setInput(value);
              }}
            >
              {label}
            </Button>
          ))}
        </div>
      </CardContent>
    </Card>
  );
};

export default SampleAddressAbiCard;
