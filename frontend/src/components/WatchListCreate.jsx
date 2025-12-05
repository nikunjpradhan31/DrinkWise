import React, { useState } from "react";
import { Button, Modal, Form } from "react-bootstrap";
import { useMovieContext } from "../context/MovieContext";

const CreateWatchlistButton = () => {
  const { createWatchlist } = useMovieContext();
  const [show, setShow] = useState(false);
  const [title, setTitle] = useState("");
  const [isPrivate, setIsPrivate] = useState(false);

  const handleSubmit = async () => {
    await createWatchlist({ watchlist_title: title, is_private: isPrivate, owner: 0, access_token: "" });
    setShow(false);
  };

  return (
    <>
      <Button onClick={() => setShow(true)}>Create Watchlist</Button>
      <Modal show={show} onHide={() => setShow(false)}>
        <Modal.Header closeButton>Create Watchlist</Modal.Header>
        <Modal.Body>
          <Form>
            <Form.Group>
              <Form.Label>Title</Form.Label>
              <Form.Control
                type="text"
                value={title}
                onChange={(e) => setTitle(e.target.value)}
              />
            </Form.Group>
            <Form.Group>
              <Form.Check
                type="checkbox"
                label="Private"
                checked={isPrivate}
                onChange={(e) => setIsPrivate(e.target.checked)}
              />
            </Form.Group>
          </Form>
        </Modal.Body>
        <Modal.Footer>
          <Button variant="secondary" onClick={() => setShow(false)}>Cancel</Button>
          <Button variant="primary" onClick={handleSubmit}>Create</Button>
        </Modal.Footer>
      </Modal>
    </>
  );
};

export default CreateWatchlistButton;
