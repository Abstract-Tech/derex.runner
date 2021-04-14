describe("Courses Page", () => {
  const lms_url = Cypress.env("LMS_URL");

  // previous test omitted for brevity
  Cypress.on("uncaught:exception", (err, runnable) => {
    // returning false here prevents Cypress from
    // failing the test
    return false;
  });
  it("test after you logged in you are able to navigate to courses page and check if there is courses or not  ", function () {
    cy.login(Cypress.env("user_email"), Cypress.env("user_password"));
    cy.visit("/courses");

    cy.get("body")
      .find(".courses-container")
      .then((res) => {
        if (res[0].children[0].classList.contains("no-course-discovery")) {
          console.log("No Courses");
        } else {
          cy.get(".course").should("be.visible");
        }
      });
  });
});
