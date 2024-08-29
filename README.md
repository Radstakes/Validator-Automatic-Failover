# Validator-Automatic-Failover
This page and associated Python scripts, detail a method for automating the failover of a Radix validator.  Firstly big thanks to Daan (Krulknul) for his contribution of the Mnemonic derivation which means that the validator owner badge can be retained in the mobile wallet, rather than held in a solely programmatic account.

All tools are provided for free to the Radix community, but if they are of benefit to you and you'd like to show some appreciation/fund further developments, please feel free to stake a little XRD on [Radstakes](https://dashboard.radixdlt.com/network-staking/validator_rdx1sds4prpgf0p25pu458fg468nw9rtwqdawwg9w45hgf0t95yd3ncs09) or send a couple of 🍺s worth of XRD to:

`account_rdx12yugeppnu2sul2qnry7nscpc9aglm922ygzkvvplp37p3rwvr4z7xz`

## Instructions

Before you start, there are some pre-requisites.  The scripts assume you are using Python3 and have only been tested on Ubuntu 22.04.  You should also ensure that your primary and backup node config has been updated with the validator address.  Please see the Radix documentation for further details.  There are also a number of dependencies which are required, these can be installed with the following commands:

`sudo apt install python3-pip`

`pip3 install radix-engine-toolkit`

`pip3 install bech32`

`pip3 install ecdsa`

`pip3 install bip_utils`

Next up, we need an account to hold the owner badge.  This can be your mobile wallet account (not a Ledger account for obvious reasons) but **you will be required to enter your seed phrase to extract the private key for the account, so please keep this in mind and be sure you're happy with the risk.  It is recommended to use a fresh seed phrase for this purpose.**

Using the following script, paste your seed phrase when prompted and copy the resultant `private_key_bytes` (you will need this in the next step) and store it securely.  You should also check that the derived address is the same account you intend to use to hold your owner badge.  If you used the seed from the mobile wallet, this should be the first account you see in the wallet.

`python3 babylon_mnemonic_to_keys.py`

Send your owner badge to the derived address (first ensuring it is as expected).  Next up, we need to edit the `autofailover.py` script with the private key from the earlier step, and add the details of the validator.  You can edit the script using any text editor, for example:

`nano autofailover.py`

Where shown in the script, paste the private_key_bytes:

`private_key_bytes_ret: bytes = <enter private key bytes here>`

Edit the following line with your own validator address:

`BABYLON_VALIDATOR_ADDRESS: str = ("validator_rdx1sds4prpgf0p25pu458fg468nw9rtwqdawwg9w45hgf0t95yd3ncs09")`

Enter the public key of your backup node here between quotes:

```
backup_public_key: bytearray = bytearray.fromhex(
        "025fb0f5e60b616ceb0dffda8c76cc580b22bacc6b9bde3ca0a487b6688f332767"
    )
```

**Warning - I wrote this script to suit my own validator (~0.5% stake) which is making around 4 proposals per epoch.  My intention here is to failover if more than 5 proposals are missed in the past 3 epochs.  Depending on your stake weight you may like to tweak the threshold or time period settings which can be found below:**

```
while missed_proposals < 6:
  response = requests.post(url1, json=data)
  response_dict = response.json()
  missed_proposals = response_dict["validators"]['items'][0]['proposals_missed']
  logging.info('Validator address: %s has missed %s proposals between current epoch: %s and past epoch: %s', BABYLON_VALIDATOR_ADDRESS, missed_proposals, current_epoch, epoch_history)
  logging.info('...Waiting for 4 mins...')
  time.sleep(240)
  response = requests.post(urlint, json=dataint)
  response_dict = response.json()
  current_epoch = response_dict["ledger_state"]["epoch"]
  epoch_history = int(current_epoch) - int(3)

if missed_proposals > 5:
  logging.info('Missed Proposals Exceed Set Limit - Failing Over Now...')
  end_epoch = int(current_epoch) + int(5)
  header: TransactionHeader = TransactionHeader(
    network_id=network_id,
    start_epoch_inclusive=current_epoch,
    end_epoch_exclusive=end_epoch,
    nonce=random_nonce(),
    notary_public_key=public_key,
    notary_is_signatory=True,
    tip_percentage=0,
  )
...
```

Once you're done editing, save the file.  The script will query the Radix gateway every minute and check for missed proposals in the past 3 epochs.  It should also be noted that any gateway can be used with this script (or even a core node for that matter) and the URL can be edited accordingly if that is the case.

Now you're ready to test the script.  Firstly we will run it locally to check it behaves as expected, and then the following steps will cover how to set this up as a systemd process so it can run in the background.

Run the script using the following command:

`python3 autofailover.py`

There may be some dependencies missed at this stage, if so just run `pip3 install...` if there's any packages you don't currently have.  If everything is working OK, the script should print the following logs:

```
INFO:Babylon Address where Owner Badge is Located: account_rdx129e74w084frkyzn2wv30d4y0l8mpvykf9af36n5akmzwe46ejaav8g
INFO:Validator Babylon Address: validator_rdx1sds4prpgf0p25pu458fg468nw9rtwqdawwg9w45hgf0t95yd3ncs09


INFO:Update Key Manifest: CALL_METHOD
    Address("account_rdx129e74w084frkyzn2wv30d4y0l8mpvykf9af36n5akmzwe46ejaav8g")
    "lock_fee"
    Decimal("10")
;
CALL_METHOD
    Address("account_rdx129e74w084frkyzn2wv30d4y0l8mpvykf9af36n5akmzwe46ejaav8g")
    "create_proof_of_non_fungibles"
    Address("resource_rdx1nfxxxxxxxxxxvdrwnrxxxxxxxxx004365253834xxxxxxxxxvdrwnr")
    Array<NonFungibleLocalId>(
        NonFungibleLocalId("[8361508c284bc2aa0795a1d28ae8f37146b701bd7390575697425eb2d08d]")
    )
;
CALL_METHOD
    Address("validator_rdx1sds4prpgf0p25pu458fg468nw9rtwqdawwg9w45hgf0t95yd3ncs09")
    "update_key"
    Bytes("025fb0f5e60b616ceb0dffda8c76cc580b22bacc6b9bde3ca0a487b6688f332767")
;

INFO:Please check manifest/addresses above for accuracy.  Validator Missed Proposals will commence logging in 30s
```

It is wise at this point to check that the script is showing the expected values for the update_key method on your validator component.  Firstly check that the first 2 lines are showing the correct account address (where the owner badge is to be located) and your validator address.

Review the transaction manifest, which should lock a fee from the account where the owner badge is, then provide a proof of the badge from this account (also ensure the badge local ID is correct here) and finally check the public key in the update_key method is correct for your backup node (reminder - ensure your validator address is in the config of your backup node first!)

After 30s, the script will begin polling the Radix Gateway and you will start to see the following logs:

```
INFO:Validator address: validator_rdx1sds4prpgf0p25pu458fg468nw9rtwqdawwg9w45hgf0t95yd3ncs09 has missed 0 proposals between current epoch: 40532 and past epoch: 40529
INFO:...Waiting for 4 minss...
INFO:Validator address: validator_rdx1sds4prpgf0p25pu458fg468nw9rtwqdawwg9w45hgf0t95yd3ncs09 has missed 0 proposals between current epoch: 40532 and past epoch: 40529
INFO:...Waiting for 4 mins...
```

Once you're happy at this stage, we can interrupt the script using `ctrl+c`.  We can then move on to running the script as a systemd service.

Firstly we need to create the service file:

`sudo nano /etc/systemd/system/autofailover.service`

Populate the file with the following (note the user name is required, along with the path to the script):

```
 [Unit]
Description=Validator Autofailover Service
After=multi-user.target
[Service]
Type=simple
User=<enter user name here>
Restart=on-failure
ExecStart=/usr/bin/python3 /path/to/autofailover.py
[Install]
WantedBy=multi-user.target
```

Restart the daemon:

`sudo systemctl daemon-reload`

Enable the service to run automatically in the event of a restart: 

`sudo systemctl enable autofailover.service`

Start the service: 

`sudo systemctl start autofailover.service`

The script should now be running in the background!  In order to check the status, use the following command which should report a status of "running":

`sudo systemctl status autofailover.service`

And finally, you can observe the logs in the terminal using the following command, which should be reporting your validators missed proposals periodically as before:

`journalctl -u autofailover.service -n 100 -f`

Congratulations, the service is now checking your node periodically for missed proposals in the past 3 epochs.  Once the threshold set has been reached, a transaction manifest to switch your validator to your backup node is created, signed and submitted to the Radix gateway.  At the next epoch rollover, your validator should automatically stop validating and your backup will take over.

**Final notes - this method has been tested on Stokenet and Mainnet, but is still experimental.  Please use at your own risk and understand that I cannot accept any responsibility for unintended consequences, loss of private keys, any funds held on your accounts or the security of your validator owner badge.  In order to sign programmatically, the private key of the account holding your validator badge needs to be exposed to the script.  You should therefore ensure that the server or host used to run the script is secure and that access to the file is protected.**
