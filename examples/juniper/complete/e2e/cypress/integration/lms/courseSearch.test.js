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
    cy.visit("/dashboard");

    cy.get("body")
      .find("#my-courses")
      .then((res) => {
        if (res.find(".empty-dashboard-message").length > 0) {
          console.log("No Courses");
        } else {
          cy.get(".course").should("be.visible");
          cy.get("li.course-item:first-child")
            .find("h3.course-title")
            .then((res) => {
              cy.get("#dashboard-search-input").type(res[0].outerText);
              cy.get(".search-button").click();
              cy.get("body")
                .find("#dashboard-search-results")
                .then((res) => {
                  if (
                    cy.get(res).children("ol.search-result-list").length > 0
                  ) {
                    cy.get("li.search-results-item").should("be.visible");
                  } else {
                    console.log("No courses founded");
                  }
                });
            });
        }
      });
  });
});
