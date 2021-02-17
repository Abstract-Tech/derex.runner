describe("Dashboard Page", () => {
  it("test after you logged in you are able to navigate to dashboard page and check if there is courses or not ", function () {
    cy.login(Cypress.env("user_email"), Cypress.env("user_password"));
    cy.visit("/dashboard");
    cy.get("body").find("ul.listing-courses").then(res => {
      if (res[0].children.length > 0) {
        cy.get(".course").should("be.visible") ;
      } else {
       alert("No Courses");
      }
    });
  });
});
  