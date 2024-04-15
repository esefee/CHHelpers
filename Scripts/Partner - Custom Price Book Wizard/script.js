
document.getElementById('addRuleGroupBtn').addEventListener('click', () => {
    const ruleGroupsDiv = document.getElementById('ruleGroups');
    const newGroup = document.createElement('div');
    newGroup.setAttribute('class', 'ruleGroup');
    newGroup.innerHTML = `
        <h3>Rule Group</h3>
        <div class="form-row">
            <label>Start Date:<input type="date" name="startDate"></label>
            <label>End Date:<input type="date" name="endDate"></label>
        </div>
        <label>Enabled:<input type="checkbox" name="enabled" checked></label>
        <div class="billingRules"></div>
        <button type="button" onclick="addBillingRule(this)">Add Billing Rule</button>
        <button type="button" onclick="removeElement(this.parentElement)">Remove Rule Group</button>
    `;
    ruleGroupsDiv.appendChild(newGroup);
});

function addBillingRule(button) {
    const billingRulesDiv = button.previousElementSibling;
    const newRule = document.createElement('div');
    newRule.setAttribute('class', 'billingRule');
    newRule.innerHTML = `
        <div class="form-row">
            <label>Name:<input type="text" name="ruleName" class="large-input" value="Billing Rule"></label>
            <label>Adjustment:<input type="number" name="billingAdjustment" class="small-input" min="0" max="100" required></label>
            <label>Rule Type:
                <select name="billingRuleType" class="small-input">
                    <option value="percentDiscount">Percent Discount</option>
                    <option value="percentIncrease">Percent Increase</option>
                    <option value="fixedRate">Fixed Rate</option>
                </select>
            </label>
        </div>
        <div class="products"></div>
        <button type="button" onclick="addProduct(this)">Add Product</button>
        <button type="button" onclick="removeElement(this.parentElement)">Remove Billing Rule</button>
    `;
    billingRulesDiv.appendChild(newRule);
    // Automatically add the first product field
    addProduct(newRule, true); // Pass true for autoAdd
}

function addProduct(button, autoAdd = false) {
    let productsDiv;
    if (autoAdd) {
        // If autoAdd is true, this means the function is called during the creation of a new rule
        productsDiv = button.getElementsByClassName('products')[0];
    } else {
        // If autoAdd is false, the function is called by button press
        productsDiv = button.previousElementSibling;
    }

    if (!productsDiv) {
        console.error("The product container div was not found.");
        return; // Stop the function if no container is found
    }

    const newProduct = document.createElement('div');
    newProduct.className = 'product';
    newProduct.innerHTML = `
        <label>Product Name:<input type="text" name="productId" value="ANY" required></label>
        <label>Include Data Transfer:<input type="checkbox" name="includeDataTransfer" checked></label>
        <label>Include RI Purchases:<input type="checkbox" name="includeRIPurchases" checked></label>
        <div class="properties"></div>
        <button type="button" onclick="addProperty(this)">Add Property</button>
        <button type="button" onclick="removeElement(this.parentElement)">Remove Product</button>
    `;
    productsDiv.appendChild(newProduct);
}

function addProperty(button) {
    const propertiesDiv = button.parentNode.querySelector('.properties');  // More reliable selector
    if (!propertiesDiv) {
        console.error("The properties container div was not found.");
        return; // Stop the function if no container is found
    }

    const newProperty = document.createElement('div');
    newProperty.className = 'property';
    newProperty.innerHTML = `
        <div class="propertyDetails">
            <label>Property Name:
                <select name="propertyName" class="small-input">
                    <option value="region">Region</option>
                    <option value="operation">Operation</option>
                    <option value="usageType">Usage Type</option>
                    <option value="lineItemDescription">Line Item Description</option>
                    <option value="instanceProperties">Instance Properties</option>
                </select>
            </label>
            <label>Value:<input type="text" name="propertyValue"></label>
        </div>
        <button type="button" onclick="removeElement(this.parentElement)">Remove Property</button>
    `;
    propertiesDiv.appendChild(newProperty);
}

function removeElement(element) {
    element.parentNode.removeChild(element);
}


function generateBillingRulesXML() {
    const createdBy = document.getElementById('createdBy').value;
    const comment = document.getElementById('comment').value;
	const currentDate = new Date();
    const formattedDate = `${(currentDate.getMonth() + 1).toString().padStart(2, '0')}/${currentDate.getDate().toString().padStart(2, '0')}/${currentDate.getFullYear()}`;
    
    let xml = '<?xml version="1.0" encoding="UTF-8"?><CHTBillingRules';

    if (createdBy) {
        xml += ` createdBy="${createdBy}"`;
    }
    xml += ` date="${formattedDate}">`;
    
   if (comment) {
        xml += `<Comment>${comment}</Comment>`;
    }
    
    const ruleGroups = document.querySelectorAll('.ruleGroup');
    
    ruleGroups.forEach(group => {
        const startDate = group.querySelector('input[name="startDate"]').value;
        const endDate = group.querySelector('input[name="endDate"]').value;
        const enabled = group.querySelector('input[name="enabled"]').checked ? 'true' : 'false';

        xml += '<RuleGroup';

        if (startDate) {
            xml += ` startDate="${startDate}"`;
        }
        if (endDate) {
            xml += ` endDate="${endDate}"`;
        }

        xml += ` enabled="${enabled}">`;

        group.querySelectorAll('.billingRule').forEach(rule => {
            const ruleName = rule.querySelector('input[name="ruleName"]').value || 'Unnamed Rule';
            const adjustment = rule.querySelector('input[name="billingAdjustment"]').value || '0';
            const ruleType = rule.querySelector('select[name="billingRuleType"]').value || 'undefined';

            xml += `<BillingRule name="${ruleName}" adjustment="${adjustment}" type="${ruleType}">`;

            rule.querySelectorAll('.product').forEach(product => {
                const productName = product.querySelector('input[name="productId"]').value || 'Generic Product';
                const includeDataTransfer = product.querySelector('input[name="includeDataTransfer"]').checked ? 'true' : 'false';
                const includeRIPurchases = product.querySelector('input[name="includeRIPurchases"]').checked ? 'true' : 'false';

                xml += `<Product productName="${productName}" includeDataTransfer="${includeDataTransfer}" includeRIPurchases="${includeRIPurchases}">`;

                product.querySelectorAll('.property').forEach(property => {
                    const propertyNameSelect = property.querySelector('select[name="propertyName"]');
                    const propertyValueInput = property.querySelector('input[name="propertyValue"]');

                    if (propertyNameSelect && propertyValueInput) {
                        const propertyName = propertyNameSelect.value;
                        const propertyValue = propertyValueInput.value;

                        if (propertyName && propertyValue) {
                            // Change the Property element to use the property name as the tag name
                            xml += `<${propertyName} name="${propertyValue}"/>`;
                        }
                    }
                });

                xml += '</Product>';
            });

            xml += '</BillingRule>';
        });

        xml += '</RuleGroup>';
    });

    xml += '</CHTBillingRules>';
    return xml;
}

// Function to generate and export the JSON
function encapsulateXMLInJSONAndExport() {
    const xml = generateBillingRulesXML(); // Call the function to generate XML
    const priceBookName = document.getElementById('priceBookName').value; // Assuming there's an input field with this ID

    // Encapsulate the generated XML in a JSON object
    const jsonEncapsulatedXML = {
	    book_name: priceBookName,
        specification: xml
    };

    // Convert the JSON object into a blob and create a URL for this blob
    const jsonData = JSON.stringify(jsonEncapsulatedXML);
    const blob = new Blob([jsonData], { type: 'application/json' });
    const url = URL.createObjectURL(blob);

    // Create an anchor element to trigger the download
    const downloadAnchorNode = document.createElement('a');
    downloadAnchorNode.href = url;
    downloadAnchorNode.download = `${priceBookName}.json`; // Use .json extension
    document.body.appendChild(downloadAnchorNode);
    downloadAnchorNode.click();
    downloadAnchorNode.remove();
}