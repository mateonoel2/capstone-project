from utils.parsers.bank_parser import get_bank_parser_result
from dotenv import load_dotenv
import pandas as pd


def main():
    load_dotenv()
    
    pd.set_option('display.max_columns', None)
    pd.set_option('display.expand_frame_repr', False)
    pd.set_option('display.max_colwidth', None)
    
    number_of_banks = 1
    
    print("Starting bank account parsing...")
    bank_results = get_bank_parser_result(number_of_banks=number_of_banks)
    
    for i, bank in enumerate(bank_results, start=1):
        print(f"\n{'='*60}")
        print(f"Bank Account {i}")
        print(f"{'='*60}")
        print(f"Owner: {bank.owner}")
        print(f"Account Number: {bank.account_number}")
        print(f"Bank Name: {bank.bank_name}")
    
    bank_data = []
    for i, bank in enumerate(bank_results, start=1):
        bank_dict = {
            'bank_number': i,
            'owner': bank.owner,
            'account_number': bank.account_number,
            'bank_name': bank.bank_name
        }
        bank_data.append(bank_dict)
    
    df_banks = pd.DataFrame(bank_data)
    print(f"\n{'='*60}")
    print("Summary DataFrame:")
    print(f"{'='*60}")
    print(df_banks)
    
    output_file = 'bank_accounts.csv'
    df_banks.to_csv(output_file, index=False)
    print(f"\n✓ Exported to {output_file}")


if __name__ == "__main__":
    main()

