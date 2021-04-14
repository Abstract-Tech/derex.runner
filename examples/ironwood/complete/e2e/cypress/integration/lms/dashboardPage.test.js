describe("Dashboard Page", () => {
  it("test after you logged in you are able to navigate to dashboard page and check if there is courses or not ", function () {
    cy.login(Cypress.env("user_email"), Cypress.env("user_password"));
    cy.visit("/dashboard");

    cy.get("body")
      .find("#my-courses")
      .then((res) => {
        if (res.find(".empty-dashboard-message").length > 0) {
          console.log("No Courses");
        } else {
          cy.get(".course").should("be.visible");
        }
      });
  });
});
