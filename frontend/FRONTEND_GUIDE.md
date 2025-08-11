# Frontend Limit Feature Guide

## 🎯 Overview

The frontend now includes a **Response Limit** dropdown that allows you to easily control how many proposals are returned from the signal discovery API.

## 📍 Location

The Response Limit dropdown is located in the **Signal Discovery** form on the main page (`http://localhost:3000`).

## 🎛️ How to Use

### Step 1: Navigate to Discovery Page
- Open your browser and go to `http://localhost:3000`
- You'll see the **Signal Discovery** form at the top

### Step 2: Fill in Search Query
- Enter your search query in the **Search Query** field
- Example: "luxury cars", "high value shoppers", "tech enthusiasts"

### Step 3: Select Response Limit
- Look for the **Response Limit** dropdown (4th column in the form)
- Click the dropdown to see available options:
  - 1 proposal
  - 2 proposals
  - 3 proposals
  - 4 proposals
  - **5 proposals (default)** ← This is the default
  - 6 proposals
  - 7 proposals
  - 8 proposals
  - 9 proposals
  - **10 proposals (max)** ← This is the maximum

### Step 4: Optional Settings
- **Principal**: Select access level (optional)
- **Platforms**: Select specific platforms (optional, hold Ctrl/Cmd for multiple)

### Step 5: Search
- Click the **🔍 Discover Signals** button
- The system will return the number of proposals you selected

## 📊 Expected Results

| Limit Selected | Proposals Returned | Notes |
|----------------|-------------------|-------|
| 1 | 1 | Minimum response |
| 3 | 3 | Custom amount |
| 5 | 5 | Default behavior |
| 8 | 8 | Custom amount |
| 10 | 10 | Maximum allowed |
| 15+ | 10 | Capped at maximum |

## 🔧 Technical Details

- **Default**: 5 proposals (if no limit specified)
- **Range**: 1-10 proposals
- **Capping**: Any value above 10 is automatically capped at 10
- **Performance**: Higher limits may take slightly longer to process due to AI generation

## 🎨 UI Layout

The form uses a responsive 4-column layout:
- **Column 1 (6/12)**: Search Query (larger for better UX)
- **Column 2 (2/12)**: Principal selection
- **Column 3 (2/12)**: Platforms selection  
- **Column 4 (2/12)**: Response Limit dropdown ← **NEW!**

## 🧪 Testing

You can test the feature by:
1. Selecting different limits from the dropdown
2. Running the same search query multiple times
3. Verifying the number of proposals returned matches your selection

The backend API automatically respects the limit you select in the frontend!

## 🐛 Debug Information

The frontend now includes a **Debug** button that allows you to view detailed technical information about your search:

### How to Access Debug Info:
1. **Perform a search** - The debug button will appear next to the search button
2. **Click the Debug button** - Shows detailed technical information
3. **Click "Hide Debug"** - Hides the debug panel

### What Debug Info Shows:
- **Validation Summary**: Number of valid/invalid proposals
- **Query & Processing**: Search details and limits
- **Ranking Method**: How signals were ranked
- **Generation Method**: How proposals were created
- **Validation Errors**: Any issues with proposal generation
- **Raw Debug Data**: Complete technical response

### Debug Button Features:
- **Smart Display**: Only appears when debug data is available
- **Error Indicators**: Shows badge with number of validation issues
- **Toggle Functionality**: Click to show/hide debug panel
- **Close Button**: X button in debug panel header to close

The debug information is hidden by default to keep the interface clean, but easily accessible when needed for troubleshooting or development.
