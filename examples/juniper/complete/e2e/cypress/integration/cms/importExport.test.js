describe("Studio Import/Export tests", () => {
  beforeEach(() => {
    cy.login_staff();
    cy.createCourse(`${Cypress.env("CMS_URL")}/home`);
    cy.get(".course-item:last-child .course-link").click();
  });

  it("A staff user can import a course", () => {
    cy.get(".nav-course-tools > .title").click();
    cy.get(".nav-course-tools-import > a").click({ force: true });

    // Upload our test course
    cy.fileUpload("importTestCourse.tar.gz");
    cy.get("#replace-courselike-button").click();

    // Wait for the upload to complete
    cy.get("#view-updated-button", { timeout: 15000 })
      .should("be.visible")
      .click();

    // Check the course content on the LMS
    // Remove the `target` attribute as we don't want it to open in a new tab
    cy.get(".view-live-button")
      .should("be.visible")
      .invoke("removeAttr", "target")
      .click({ force: true });
    cy.url().should("contain", "/courses/");
    cy.get("body").should(
      "contain",
      "This course purpose is to be imported in a Cypress test."
    );
  });

  it("A staff user can export a course", () => {
    cy.get(".nav-course-tools > .title").click();
    cy.get(".nav-course-tools-export > a").click({ force: true });

    // Export the course
    cy.get(".title > .list-actions > .item-action > .action")
      .trigger("pointerover")
      .wait(1000)
      .click();
    cy.get(".item-progresspoint-success > .status-detail > .title", {
      timeout: 15000,
    }).should("have.css", "color", "rgb(0, 129, 0)");

    // We need to stop cypress waiting for the page to load after the file is downloaded
    // https://github.com/cypress-io/cypress/issues/14857
    cy.window()
      .document()
      .then(function (document) {
        document.addEventListener("click", () => {
          setTimeout(function () {
            document.location.reload();
          }, 5000);
        });
        cy.get("#download-exported-button").click();
      });

    // If there is a way to check if the zipfile downloaded successfully
    // or it's contents i still have to find it
  });
});
