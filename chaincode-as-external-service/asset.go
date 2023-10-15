package main

type SimpleAsset struct {
	TxID    			string `json:"txID"`
	UID 				string `json:"uid"`
	DESTINATION_UID		string `json:"destination_uid"`
	DESTINATION_TYPE	string `json:"destination_type"`
	TransactionID 		string `json:"transaction_id"`
	TransactionType 	string `json:"transaction_type"`
	TransactionAmount 	string `json:"transaction_amount"`
	TransactionDateTime string `json:"transaction_date_time"`
}