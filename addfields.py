import boto3
import json

# Initialize QuickSight client
quicksight = boto3.client('quicksight', region_name='us-east-1')

# Define your dataset details
dataset_id = '0e071154-20f6-4be2-96a2-7d8d0023c735'
aws_account_id = '648953653967'

# Define your calculated fields
calculated_fields = [
    {
        "Name": "Completed",
        "Expression": 'ifelse(isNull(sumIf({Annual Savings},status="Completed")=1),0,sumIf({Annual Savings},status="Completed"))',
        "DataType": "DECIMAL"
    },
    {
        "Name": "Resource Fixed",
        "Expression": 'ifelse(isNull(sumIf({Annual Savings},status="Resource Fixed")=1),0,sumIf({Annual Savings},status="Resource Fixed"))',
        "DataType": "DECIMAL"
    },
    {
        "Name": "Weekly Cost of Inaction",
        "Expression": '({Annual Savings}*7/365)',
        "DataType": "DECIMAL"
    },
    {
        "Name": "Manually Fixed",
        "Expression": 'ifelse(isNull(sumIf({Annual Savings},status="Manually Fixed")=1),0,sumIf({Annual Savings},status="Manually Fixed"))',
        "DataType": "DECIMAL"
    },
    {
        "Name": "Completed Savings",
        "Expression": '{Resource Fixed}+{Manually Fixed}+Completed',
        "DataType": "DECIMAL"
    },
    {
        "Name": "Potential Savings",
        "Expression": 'ifelse(isNull(sumIf({Annual Savings},status="Manual Approval")=1),0,sumIf({Annual Savings},status="Manual Approval"))',
        "DataType": "DECIMAL"
    },
    {
        "Name": "Percentage Complete",
        "Expression": 'ifelse(isNull((Completed+{Manually Fixed}+{Resource Fixed})/({Potential Savings}+Completed+{Manually Fixed}+{Resource Fixed}))=1,0,((Completed+{Manually Fixed}+{Resource Fixed})/({Potential Savings}+(Completed+{Manually Fixed}+{Resource Fixed}))))',
        "DataType": "DECIMAL"
    },
    {
        "Name": "Savings Found",
        "Expression": '{Completed Savings}+{Potential Savings}',
        "DataType": "DECIMAL"
    },
    {
        "Name": "NewRecDate",
        "Expression": 'formatDate({created_at}, \'YYYY-MM\')',
        "DataType": "DATETIME"
    },
    {
        "Name": "RunningPotentialSavings",
        "Expression": 'runningSum({Potential Savings}, [NewRecDate ASC])',
        "DataType": "DECIMAL"
    },
    {
        "Name": "RunningCompletedSavings",
        "Expression": 'runningSum({Completed Savings}, [NewRecDate ASC])',
        "DataType": "DECIMAL"
    },
    {
        "Name": "ApprovedFixers",
        "Expression": 'countIf({Catalogue Status},{Catalogue Status}="APPROVED")',
        "DataType": "INTEGER"
    },
    {
        "Name": "UnapprovedFixers",
        "Expression": 'countIf({Catalogue Status},{Catalogue Status}="PENDING")',
        "DataType": "INTEGER"
    },
    {
        "Name": "ManualFixers",
        "Expression": 'countIf({Catalogue Status},{Catalogue Status}="Manual Fix")',
        "DataType": "INTEGER"
    }
]

# Get the current dataset definition
response = quicksight.describe_data_set(
    AwsAccountId=aws_account_id,
    DataSetId=dataset_id
)

dataset_definition = response['DataSet']

# Add calculated fields to the dataset definition
for field in calculated_fields:
    dataset_definition['LogicalTableMap']['LogicalTable']['Source']['CalculatedColumns'].append({
        'Name': field['Name'],
        'Expression': field['Expression'],
        'DataType': field['DataType']
    })

# Update the dataset with new calculated fields
try:
    response = quicksight.update_data_set(
        AwsAccountId=aws_account_id,
        DataSetId=dataset_id,
        Name=dataset_definition['Name'],
        PhysicalTableMap=dataset_definition['PhysicalTableMap'],
        LogicalTableMap=dataset_definition['LogicalTableMap'],
        ImportMode=dataset_definition['ImportMode']
    )
    print("Dataset updated successfully")
except Exception as e:
    print(f"Error updating dataset: {str(e)}")