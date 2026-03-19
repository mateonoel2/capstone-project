"use client";

import * as React from "react";
import { Check, ChevronsUpDown } from "lucide-react";

import { cn } from "@/lib/utils";
import { Button } from "@/components/ui/button";
import {
  Popover,
  PopoverContent,
  PopoverTrigger,
} from "@/components/ui/popover";
import { Input } from "@/components/ui/input";
import { Bank } from "@/lib/api";
import { useT } from "@/lib/i18n";

interface BankComboboxProps {
  banks: Bank[];
  value: string;
  onChange: (value: string) => void;
  className?: string;
}

export function BankCombobox({ banks, value, onChange, className }: BankComboboxProps) {
  const [open, setOpen] = React.useState(false);
  const [search, setSearch] = React.useState("");
  const t = useT();

  const filteredBanks = React.useMemo(() => {
    if (!search) return banks;
    return banks.filter((bank) =>
      bank.name.toLowerCase().includes(search.toLowerCase())
    );
  }, [banks, search]);

  const handleSelect = (bankName: string) => {
    onChange(bankName);
    setOpen(false);
    setSearch("");
  };

  return (
    <Popover open={open} onOpenChange={setOpen}>
      <PopoverTrigger asChild>
        <Button
          variant="outline"
          role="combobox"
          aria-expanded={open}
          className={cn("w-full justify-between", className)}
        >
          {value || t("bankCombobox.selectBank")}
          <ChevronsUpDown className="ml-2 h-4 w-4 shrink-0 opacity-50" />
        </Button>
      </PopoverTrigger>
      <PopoverContent className="w-[--radix-popover-trigger-width] p-0">
        <div className="flex flex-col">
          <div className="border-b p-2">
            <Input
              placeholder={t("bankCombobox.searchBank")}
              value={search}
              onChange={(e) => setSearch(e.target.value)}
              className="h-9"
            />
          </div>
          <div className="max-h-[300px] overflow-y-auto">
            {filteredBanks.length === 0 ? (
              <div className="py-6 text-center text-sm text-muted-foreground">
                {t("bankCombobox.noResults")}
              </div>
            ) : (
              <div className="p-1">
                {filteredBanks.map((bank) => (
                  <button
                    key={bank.code}
                    onClick={() => handleSelect(bank.name)}
                    className={cn(
                      "relative flex w-full cursor-pointer select-none items-center rounded-sm px-2 py-1.5 text-sm outline-none transition-colors hover:bg-accent hover:text-accent-foreground",
                      value === bank.name && "bg-accent text-accent-foreground"
                    )}
                  >
                    <Check
                      className={cn(
                        "mr-2 h-4 w-4",
                        value === bank.name ? "opacity-100" : "opacity-0"
                      )}
                    />
                    {bank.name}
                  </button>
                ))}
              </div>
            )}
          </div>
        </div>
      </PopoverContent>
    </Popover>
  );
}
