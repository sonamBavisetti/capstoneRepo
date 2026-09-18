Feature: Product search and filter in product catalog (VNK-2)
  As a customer
  I want to search and filter products
  So that I can find the products I need quickly

  # Traceability:
  # - Jira: VNK-2
  # - Requirements: FR-02 (Product listing page shows products with required fields)

  Scenario: View products list includes total count header
    Given the API is running
    When I request the products list
    Then I should receive a 200 response
    And the response header "X-Total-Count" should be present

  Scenario: Search query matches across product name/category/specifications
    Given the API is running
    When I request the products list with query "Business"
    Then I should receive a 200 response
    And the response header "X-Total-Count" should be present
    And the response should include at least one product with name containing "Business"

  Scenario: Filters intersect to narrow results
    Given the API is running
    When I request the products list filtered by category "Stationery" and material "PVC"
    Then I should receive a 200 response
    And every returned product should have category "Stationery"
    And every returned product should have material "PVC"

  Scenario: Invalid material filter returns validation error
    Given the API is running
    When I request the products list filtered by material "WOOD"
    Then I should receive a 400 response
    And the response JSON should contain an "error" field
