import os
import sys
import json
import requests
import qrcode

"""
    Script to save the invoice as qrcode and re-query same r_hash.
    Needs dev-dependencies to run.
"""

def initial_query(
        query="What is the capital of France?"
    ):

    try:

        r = requests.post(
            url="http://localhost:5000/query",
            headers={'Content-Type': 'application/json'},
            data=json.dumps({"query": query}),
        )

        query_data = r.json()

        invoice = query_data.get("invoice")
        r_hash = query_data.get("r_hash")

        fn = f"invoice-{r_hash[:4]}.png"
        print("Saving invoice to", fn)
              
        qrcode.make(invoice).save(fn)

        return query_data

    except Exception as e:
        print(e) 
        

def follow_query(
        r_hash,
    ):

    try:

        r = requests.post(
            url="http://localhost:5000/query",
            headers={'Content-Type': 'application/json'},
            data=json.dumps({"r_hash": r_hash}),
        )

        try:
            return r.json()
        except:
            return r.text
        

    except Exception as e:
        print(e)




if __name__ == "__main__":
    
    initial_data = initial_query()
    
    if not(isinstance(initial_data, dict)):
        print("No initial query data returned, exiting...")
        print(str(initial_data)[:100])  # print any error message
        sys.exit(1)

    print(f"""
          Now open invoice-xxxx.png and pay the invoice.
          You can use VScode to open the file.
          Now we'll enter a loop that checks payment of 
            r_hash: {initial_data.get("r_hash", "????")[:4]}
          Use control-c to exit the loop.
    """)

    NO_PAY_MSG = "Payment Required"
    WAS_USED_MSG = "Payment already used"
    
    PROMPT_MSG = "\nPress enter to continue and check payment, <q> to exit...\n"
    
    is_looping = True

    while is_looping:    

        try:
            
            s = input(PROMPT_MSG)

            if s == "q":
                is_looping = False
                continue
            
            follow_data = follow_query(initial_data.get("r_hash"))
            
            result_msg = ""
            if isinstance(follow_data, dict):
                if follow_data.get("message") == NO_PAY_MSG: 
                    result_msg = "invoice not paid yet"
                elif follow_data.get("message") == WAS_USED_MSG:
                    result_msg = "invoice already paid"
                else:
                    result_msg = "query result:"
            else:
                result_msg = "abberant response, not json"
            
            print(result_msg)
            print(follow_data)
                    
        except KeyboardInterrupt:        
            is_looping = False

        except Exception as e:
            print(e)
            

    print("Exiting client.py...")