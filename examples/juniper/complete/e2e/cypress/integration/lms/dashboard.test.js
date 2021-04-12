describe("Knowledge Base Application", () => {
  const lms_url = Cypress.env("LMS_URL");

  // previous test omitted for brevity
  it("test after you logged in you are able to navigate to dashboard page and check if there is courses or not ", function () {
    cy.login(Cypress.env("user_email"), Cypress.env("user_password"));

    cy.visit("/dashboard");

    cy.get("body").find("#my-courses").then(res => {
      if (res.find(".empty-dashboard-message").length > 0 && res.find("ul.listing-courses")[0].children.length == 0) {
        console.log("No Courses");
      } else {
        cy.get(".course").should("be.visible") ;
      }
    });
  });
})
