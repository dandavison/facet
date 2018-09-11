;;; facet.el --- work on a facet
;; Version: 0.0.0
;; Author: dandavison7@gmail.com
;; Keywords: project, task
;; URL: https://github.com/dandavison/facet

(require 's)
(require 'helm)

(defvar facet-directory (expand-file-name "~/.facet/"))

;;;###autoload
(defun facet-show ()
  (interactive)
  (shell-command "facet show"))

;;;###autoload
(defun facet-workon ()
  "Set current facet."
  (interactive)
  (helm
   :sources
   `((name . "Facets")
     (candidates . ,(facet-candidates-list))
     (action . (lambda (candidate)
                 (shell-command (format "facet notes %s" candidate)))))))

;;;###autoload
(defun facet-cd (&optional arg)
  "Open dired buffer on facet directory"
  (interactive "P")
  (let ((facet (if (not arg) (facet-current-facet)
                 (helm :sources
                       `((name . "Facets")
                         (candidates . ,(facet-candidates-list)))))))
    (dired (expand-file-name facet (facet-facets-directory)))))

(defun facet-candidates-list ()
  "Return alist of facets
  Each element is ((formatted-line) . facet-name)"
  (let* ((rows
          (mapcar
           (lambda (line) (split-string line "\t"))
           (split-string
            (s-chomp
             (ansi-color-apply (shell-command-to-string "facet ls"))) "\n")))
         (left-column-width
          (apply #'max (mapcar (lambda (row) (length (car row))) rows)))
         (left-column-fmt (format "%%-%ds %%s" left-column-width)))
    (mapcar
     (lambda (row)
       `(,(format left-column-fmt (car row) (or (cadr row) ""))
         .
         ,(car row)))
     rows)))

(defun facet-current-facet ()
  (cdr (assoc 'facet (facet-read-state))))

(defun facet-facets-directory ()
  (expand-file-name "facets" facet-directory))

(defun facet-state-file ()
  (expand-file-name "state.json" facet-directory))

(defun facet-read-state ()
  (json-read-file (facet-state-file)))

(defun facet-write-state (key value)
  (write-region
   (json-encode
    (append
     (assq-delete-all key (facet-read-state))
     `((,key . ,value))))
   nil (facet-state-file)))


(provide 'facet)
;;; facet.el ends here
