describe("Knowledge Base Application", () => {
  const lms_url = Cypress.env("LMS_URL");

  // previous test omitted for brevity
  Cypress.on("uncaught:exception", (err, runnable) => {
    // returning false here prevents Cypress from
    // failing the test
    return false;
  });
  it("As a logged in user I should be able to access the courseware of a course i’m enrolled in", function() {
    cy.login(Cypress.env("user_email"), Cypress.env("user_password"));
    cy.visit("/courses");

    cy.get("body").find("ul.courses-listing.courses-list").then(res => {
      if (res[0].children.length > 0) {
        //// do task that you want to perform
        cy.get(".course") ;
      } else {
        console.log("No Courses");
      }
    });
  });
});
