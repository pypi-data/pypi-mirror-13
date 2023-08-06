<html>
  <body>
    <h3>Data Import Warnings (<code>${command}</code>)</h3>
    % if dry_run:
        <p>
          <em><strong>NOTE:</strong>&nbsp; This was a dry run only; no data was harmed
          in the making of this email.</em>
        </p>
    % endif
    <p>
      Generally the periodic data import is expected to be a precaution only, in order
      to detect and fix Rattail data which falls out of sync from the data authority,
      e.g. your POS.&nbsp; It is normally expected that proper real-time operation
      <em>should</em> be enough to keep things in sync; therefore any actual changes
      which occur as part of this import process are considered "warnings".
    </p>
    <p>
      The following is a list of changes which occurred during the latest
      import run.&nbsp; Please investigate at your convenience.
    </p>
    <ul>
      % for model, (created, updated, deleted) in updates.iteritems():
          <li>
            <a href="#${model}">${model}</a>
            - ${len(created)} created, ${len(updated)} updated, ${len(deleted)} deleted
          </li>
      % endfor
    </ul>
    % for model, (created, updated, deleted) in updates.iteritems():
        <h4><a name="${model}">${model}</a></h4>
        % for label, records in (('created', created), ('updated', updated), ('deleted', deleted)):
            % if records:
                % if len(records) == 1:
                    <p>1 record was <strong>${label}:</strong></p>
                % else:
                    <p>${len(records)} records were <strong>${label}:</strong></p>
                % endif
                <ul>
                  % for record in records:
                      <li>${render_record(record)}</li>
                  % endfor
                </ul>
            % endif
        % endfor
    % endfor
  </body>
</html>
