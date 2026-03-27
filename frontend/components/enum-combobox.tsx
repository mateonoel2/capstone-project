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
import { useT } from "@/lib/i18n";

interface EnumComboboxProps {
  options: string[];
  value: string;
  onChange: (value: string) => void;
  placeholder?: string;
  className?: string;
}

export function EnumCombobox({ options, value, onChange, placeholder, className }: EnumComboboxProps) {
  const [open, setOpen] = React.useState(false);
  const [search, setSearch] = React.useState("");
  const t = useT();

  const filtered = React.useMemo(() => {
    if (!search) return options;
    return options.filter((opt) =>
      opt.toLowerCase().includes(search.toLowerCase())
    );
  }, [options, search]);

  const handleSelect = (opt: string) => {
    onChange(opt);
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
          className={cn("w-full justify-between font-normal", className)}
        >
          {value || placeholder || t("enumCombobox.select")}
          <ChevronsUpDown className="ml-2 h-4 w-4 shrink-0 opacity-50" />
        </Button>
      </PopoverTrigger>
      <PopoverContent className="w-[--radix-popover-trigger-width] p-0">
        <div className="flex flex-col">
          <div className="border-b p-2">
            <Input
              placeholder={t("enumCombobox.search")}
              value={search}
              onChange={(e) => setSearch(e.target.value)}
              className="h-9"
            />
          </div>
          <div className="max-h-[300px] overflow-y-auto">
            {filtered.length === 0 ? (
              <div className="py-6 text-center text-sm text-muted-foreground">
                {t("enumCombobox.noResults")}
              </div>
            ) : (
              <div className="p-1">
                {filtered.map((opt) => (
                  <button
                    key={opt}
                    type="button"
                    onClick={() => handleSelect(opt)}
                    className={cn(
                      "relative flex w-full cursor-pointer select-none items-center rounded-sm px-2 py-1.5 text-sm outline-none transition-colors hover:bg-accent hover:text-accent-foreground",
                      value === opt && "bg-accent text-accent-foreground"
                    )}
                  >
                    <Check
                      className={cn(
                        "mr-2 h-4 w-4",
                        value === opt ? "opacity-100" : "opacity-0"
                      )}
                    />
                    {opt}
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
